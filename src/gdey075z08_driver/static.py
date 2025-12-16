from pydantic_settings import BaseSettings


class Static:
    #: int Display resolution
    EPD_WIDTH: int = 800
    EPD_HEIGHT: int = 480

    #: int EPD7IN5 commands
    PANEL_SETTING: int = 0x00
    POWER_SETTING: int = 0x01
    POWER_OFF: int = 0x02
    POWER_OFF_SEQUENCE_SETTING: int = 0x03
    POWER_ON: int = 0x04
    POWER_ON_MEASURE: int = 0x05
    BOOSTER_SOFT_START: int = 0x06
    DEEP_SLEEP: int = 0x07
    DATA_START_TRANSMISSION_1: int = 0x10
    DATA_STOP: int = 0x11
    DISPLAY_REFRESH: int = 0x12
    DATA_START_TRANSMISSION_2: int = 0x13
    LUT_FOR_VCOM: int = 0x20
    LUT_BLUE: int = 0x21
    LUT_WHITE: int = 0x22
    LUT_GRAY_1: int = 0x23
    LUT_GRAY_2: int = 0x24
    LUT_RED_0: int = 0x25
    LUT_RED_1: int = 0x26
    LUT_RED_2: int = 0x27
    LUT_RED_3: int = 0x28
    LUT_XON: int = 0x29
    PLL_CONTROL: int = 0x30
    TEMPERATURE_SENSOR_COMMAND: int = 0x40
    TEMPERATURE_CALIBRATION: int = 0x41
    TEMPERATURE_SENSOR_WRITE: int = 0x42
    TEMPERATURE_SENSOR_READ: int = 0x43
    VCOM_AND_DATA_INTERVAL_SETTING: int = 0x50
    LOW_POWER_DETECTION: int = 0x51
    TCON_SETTING: int = 0x60
    TCON_RESOLUTION: int = 0x61
    SPI_FLASH_CONTROL: int = 0x65
    REVISION: int = 0x70
    GET_STATUS: int = 0x71
    AUTO_MEASUREMENT_VCOM: int = 0x80
    READ_VCOM_VALUE: int = 0x81
    VCM_DC_SETTING: int = 0x82
