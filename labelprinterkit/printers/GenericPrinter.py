from typing import List

from .BasePrinter import BasePrinter, BackendType
from .Status import Status
from .logger import logger
from .tools import encode_line
from ..backends import UniDirectionalBackend
from ..commands.AdvancedModeSettings import AdvancedModeSettings
from ..commands.Initialize import Initialize
from ..commands.Invalidate import Invalidate
from ..commands.Print import Print
from ..commands.PrintInformation import PrintInformation
from ..commands.RasterGraphicsTransfer import RasterGraphicsTransfer
from ..commands.SelectCompressionMode import SelectCompressionMode
from ..commands.SpecifyCutEachPages import SpecifyCutEachPages
from ..commands.SpecifyMarginAmount import SpecifyMarginAmount
from ..commands.StatusInformationRequest import StatusInformationRequest
from ..commands.SwitchDynamicCommandMode import SwitchDynamicCommandMode
from ..commands.VariousModeSettings import VariousModeSettings
from ..commands.ZeroRasterGraphics import ZeroRasterGraphics
from ..constants import Resolution, Media, PrintHeadHeight, PRINTHEAD_MEDIA_ALIGNMENT
from ..job import Job


class GenericPrinter(BasePrinter):
    _SUPPORTED_RESOLUTIONS = (Resolution.LOW, Resolution.HIGH)
    _FEATURE_HALF_CUT = True
    _PRINT_HEAD_HEIGHT = PrintHeadHeight.PHH128

    def __init__(self, backend: BackendType):
        super().__init__(backend)

    def reset(self):
        self._backend.write(Invalidate() * 100)  # Invalidate command
        self._backend.write(Initialize())  # Initialize command 1b 40

    def get_status(self) -> Status:
        if hasattr(self._backend, 'get_status'):
            data = self._backend.get_status()
        elif isinstance(self._backend, UniDirectionalBackend):
            raise RuntimeError("Backend is unidirectional")
        else:
            self.reset()
            self._backend.write(StatusInformationRequest())
            data = self._backend.read(32)
        if not data:
            raise IOError("No Response from printer")

        if len(data) < 32:
            raise IOError("Invalid Response from printer")

        return Status(data)

    def print(self, job: Job):
        try:
            phma = PRINTHEAD_MEDIA_ALIGNMENT[(self._PRINT_HEAD_HEIGHT, job.media)]
        except KeyError:
            raise RuntimeError('Unsupported Media')

        logger.info("starting print")

        self.reset()

        if job.media in (Media.NO_MEDIA, Media.UNSUPPORTED_MEDIA):
            raise RuntimeError('Unsupported Media')

        if job.resolution not in self._SUPPORTED_RESOLUTIONS:
            raise RuntimeError('Resolution is not supported by this printer.')

        various_modes: List[VariousModeSettings.Settings] = list()
        if job.auto_cut:
            various_modes.append(VariousModeSettings.Settings.AUTO_CUT)
        if job.mirror_printing:
            various_modes.append(VariousModeSettings.Settings.MIRROR_PRINTING)
        various_mode_command = VariousModeSettings(various_modes)

        advanced_modes: List[AdvancedModeSettings.Settings] = list()
        if job.half_cut:
            if not self._FEATURE_HALF_CUT:
                raise RuntimeError('Half cut is not supported by this printer.')
            advanced_modes.append(AdvancedModeSettings.Settings.HALF_CUT)
        if not job.chain:
            advanced_modes.append(AdvancedModeSettings.Settings.NO_CHAIN_PRINTING)
        if job.special_tape:
            advanced_modes.append(AdvancedModeSettings.Settings.SPECIAL_TAPE)
        if job.resolution == Resolution.HIGH:
            margin = 30
            advanced_modes.append(AdvancedModeSettings.Settings.HIGH_RESOLUTION)
        else:
            margin = 15
        advanced_mode_command = AdvancedModeSettings(advanced_modes)
        specify_margin_command = SpecifyMarginAmount(margin)

        cut_each_command = SpecifyCutEachPages(job.cut_each)

        for i, pagedata in enumerate(job):
            # switch dynamic command mode: enable raster mode
            self._backend.write(SwitchDynamicCommandMode(SwitchDynamicCommandMode.Modes.RASTER))

            # Print information command
            page: PrintInformation.Page = PrintInformation.Page.OTHER_PAGE
            if i == 0:
                page = PrintInformation.Page.STARTING_PAGE
            if i == len(job) - 1:
                page = PrintInformation.Page.LAST_PAGE

            information_command = PrintInformation(
                media_type=job.media.value.media_type,
                high_resolution=job.resolution == Resolution.HIGH,
                media_width=job.media.value.width,
                page=page,
            )

            self._backend.write(information_command)
            if i == 0 and job.auto_cut:
                # Ugly workaround
                # Print information command a second time forces cutting after first page.
                # No idea why this is needed, but it works
                self._backend.write(information_command)

            # Various mode
            self._backend.write(various_mode_command)

            # Advanced mode
            self._backend.write(advanced_mode_command)

            # margin
            self._backend.write(specify_margin_command)

            if job.auto_cut:
                # Configure after how many pages a cut should be done
                self._backend.write(cut_each_command)

            # Enable compression mode
            self._backend.write(SelectCompressionMode(SelectCompressionMode.Compression.TIFF))

            # send rastered lines
            for line in pagedata:
                logger.debug(f"line: {line}")
                self._backend.write(
                    RasterGraphicsTransfer(
                        encode_line(
                            line,
                            phma,
                            self._PRINT_HEAD_HEIGHT
                        )
                    )
                )

            self._backend.write(ZeroRasterGraphics())

            logger.debug(f"i: {i}")
            if i < len(job) - 1:
                self._backend.write(Print())

        # end page
        self._backend.write(Print(feed=True))
        logger.info("end of page")
