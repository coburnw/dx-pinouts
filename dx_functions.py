
# pip install v-palette
# for palette colors selection, view  https://github.com/villoro/vpalette

from pinoutOverview import FunctionLabel, Functions
from v_palette import get_colors

palette = 'flat'

class SignalFunctionFactory():
    def __new__(cls, signal):
        # get function type and peripheral index
        ftype, partition, suffix = signal.function.partition('_')
        ftype = ftype.rstrip('0123456789').lower()

        if ftype in ['tca','tcb','tcd']:
            return PwmSignalFunction(signal=signal)

        if ftype in['tca']:
            return TcaSignalFunction(signal=signal)

        if ftype in['tcb']:
            return TcbSignalFunction(signal=signal)

        if ftype in['tcd']:
            return TcdSignalFunction(signal=signal)
        
        if ftype in['ptc']:
            return PtcSignalFunction(signal=signal)
        
        if ftype in ['ain', 'dac', 'vrefa']:
            return AnalogSignalFunction(signal=signal)

        if ftype in['opamp']:
            return OpampSignalFunction(signal=signal)

        if ftype in ['ac', 'zcd']:
            return ComparatorSignalFunction(signal=signal)

        if ftype in ['usart']:
            return AsyncSerialSignalFunction(signal=signal)
                    
        if ftype in ['twi', 'spi', 'i2c']:
            return SyncSerialSignalFunction(signal=signal)
                    
        if ftype in ['ccl', 'evsys']:
            return LogicSignalFunction(signal=signal)
            
        if ftype in ['clkctrl', 'other', 'updi']:
            return SystemSignalFunction(signal=signal)

        if ftype in ['ioport']:
            return SkipSignalFunction(signal=signal)

        return OtherSignalFunction(signal=signal)
    
class PinFunctionFactory():
    def __new__(cls, pin_name):
        # get function type and peripheral index
        ftype = pin_name.rstrip('0123456789').lower()

        if ftype in ['vddio']:
            return MvioVddPinFunction(pin_name)

        if ftype.startswith('pc'):
            return MvioPortPinFunction(pin_name)
        
        if ftype.startswith('p'): # in ['port']:
            return PortPinFunction(pin_name)
        
        if ftype in ['agnd', 'gnd']:
            return VssPinFunction(pin_name)

        if ftype in ['avdd', 'vdd']:
            return VddPinFunction(pin_name)

        if ftype in ['updi']:
            return SystemPinFunction(pin_name)

        return OtherPinFunction(pin_name)


sort_index = 0
class DxFunction(FunctionLabel):
    # DxFunction parses the atpack signal to properties that
    # the Function base class can make use of.
    type_index = sort_index

    @property
    def text(self):
        # the text to be displayed inside a function label
        # typically overridden by the function specialization
        return self.name

    def parse_function(self, function):
        inst_name, partition, alt_pos = function.partition('_ALT')

        name = inst_name.rstrip('0123456789')
        instance = inst_name.replace(name, '')

        try:
            instance = int(instance)
        except ValueError:
            instance = 0

        try:
            alt_pos = int(alt_pos)
        except ValueError:
            alt_pos = 0

        return name, instance, alt_pos


class DxSignalFunction(DxFunction):
    def __init__(self, signal):
        super().__init__()

        self.signal = signal
        self.width = 100

        return

    @property
    def text(self):
        inst = ''
        if self.instance > 0:
            inst = '{}'.format(self.instance)

        alt = ''
        if self.alt_position > 0:
            alt = '/{}'.format(self.alt_position)

        text = '{}{}{}'.format(self.signal.group, inst, alt)

        return text

    @property
    def name(self):
        name, instance, alt_pos = self.parse_function(self.signal.function)
        return name

    @property
    def instance(self):
        name, instance, alt_pos = self.parse_function(self.signal.function)
        return int(instance)

    @property
    def is_alt(self):
        name, instance, alt_pos = self.parse_function(self.signal.function)
        return int(alt_pos) > 0

    @property
    def alt_position(self):
        name, instance, alt_pos = self.parse_function(self.signal.function)
        return int(alt_pos)

    @property
    def footnote(self):
        return None  # self.function.get('footnote', None)

    @property
    def pad_name(self):
        return self.signal.pad  # [1]


class DxPinFunction(DxFunction):
    # DxFunction parses the atpack signal to properties that
    # the Function base class can make use of.
    def __init__(self, pin_name):
        super().__init__()

        self.pin_name = pin_name

        return

    @property
    def text(self):
        name = '{}'.format(self.name)
        return name

    @property
    def name(self):
        return self.pin_name

    @property
    def is_alt(self):
        return False

    @property
    def alt_position(self):
        return 0

    @property
    def instance(self):
        return 0

    @property
    def footnote(self):
        return None


sort_index += 1
class PortPinFunction(DxPinFunction):
    type_index = sort_index

    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'PIN'
        self.description = 'PORT PIN'

        self.box_style['stroke'] = get_colors(('green', 900), palette=palette)
        self.box_style['fill'] = get_colors(('green', 700), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return


sort_index += 1
class MvioPortPinFunction(DxPinFunction):
    type_index = sort_index
    
    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'MVIO Pin'
        self.description = 'PORT PIN'

        self.box_style['stroke'] = get_colors(('green', 900), palette=palette)
        self.box_style['fill'] = get_colors(('green', 700), palette=palette)

        self.text_style['stroke'] = get_colors(('black', 200), palette=palette)
        self.text_style['fill'] = get_colors(('black', 200), palette=palette)

        return


sort_index += 1
class MvioVddPinFunction(DxPinFunction):
    type_index = sort_index

    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'MVIO VDD'
        self.description = 'MULTI-VOLTAGE PIN'

        self.box_style['stroke'] = get_colors(('red', 800), palette=palette)
        self.box_style['fill'] = get_colors(('red', 600), palette=palette)

        self.text_style['stroke'] = get_colors(('black', 800), palette=palette)
        self.text_style['fill'] = get_colors(('black', 800), palette=palette)

        return

sort_index += 1
class VssPinFunction(DxPinFunction):
    type_index = sort_index
    
    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'Ground'
        self.description = 'GROUND'

        self.box_style['stroke'] = get_colors(('black', 200), palette=palette)
        self.box_style['fill'] = get_colors(('black', 200), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return

sort_index += 1
class VddPinFunction(DxPinFunction):
    type_index = sort_index
    
    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'Power'
        self.description = 'POWER'

        self.box_style['stroke'] = get_colors(('red', 800), palette=palette)
        self.box_style['fill'] = get_colors(('red', 600), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return


sort_index += 1
class SystemPinFunction(DxPinFunction):
    type_index = sort_index

    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'System'
        self.description = 'System'

        self.box_style['stroke'] = '#CCAA00'
        self.box_style['fill'] = '#FFE97C'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return


sort_index += 1
class OtherPinFunction(DxPinFunction):
    type_index = sort_index

    def __init__(self, pin_name):
        super().__init__(pin_name)

        self.title = 'Other'
        self.description ='OTHER'

        self.box_style['stroke'] = get_colors(('black', 800), palette=palette)
        self.box_style['fill'] = get_colors(('white', 600), palette=palette)

        self.text_style['stroke'] = get_colors(('black', 800), palette=palette)
        self.text_style['fill'] = get_colors(('black', 800), palette=palette)

        return


sort_index += 1
class PtcSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'Touch'
        self.description = 'Touch'

        self.box_style['stroke'] = get_colors(('brown', 700), palette=palette)
        self.box_style['fill'] = get_colors(('brown', 300), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return

    @property
    def text(self):
        name = '{}.{}'.format(self.signal.group, self.signal.index)
        return name

sort_index += 1
class AnalogSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'Analog'
        self.description = 'ADC/DAC'

        self.box_style['stroke'] = get_colors(('brown', 700), palette=palette)
        self.box_style['fill'] = get_colors(('brown', 500), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return

    @property
    def text(self):
        name = self.name
        if 'AIN' in name:
            name = 'ADC.{}'.format(self.signal.index)
        elif 'DAC' in name:
            name = 'DAC.{}'.format(self.signal.index)
        elif 'PTC' in name:
            pass
        elif 'VREF' in name:
            pass
        
        return name

sort_index += 1
class OpampSignalFunction(DxSignalFunction):
    type_index = sort_index

    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'OpAmp'
        self.description = 'OPAMP'

        self.box_style['stroke'] = get_colors(('green', 700), palette=palette)
        self.box_style['fill'] = get_colors(('green', 500), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return

    @property
    def text(self):
        text = self.signal.group
        if 'INP' in text:
            text = text.replace('INP', '.IN+')
        elif 'INN' in text:
            text = text.replace('INN', '.IN-')
        elif 'OUT' in text:
            text = text.replace('OUT', '.OUT')
            
        return text

sort_index += 1
class AsyncSerialSignalFunction(DxSignalFunction):
    type_index = sort_index

    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'USART'
        self.description = 'Universal Serial Interface'

        self.box_style['stroke'] = get_colors(('blue', 800), palette=palette)
        self.box_style['fill'] = get_colors(('blue', 400), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 500), palette=palette)
        self.text_style['fill'] = get_colors(('white', 500), palette=palette)

        return

sort_index += 1
class SyncSerialSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'SPI/TWI'
        self.description = 'Syncronous Serial Interface'

        self.box_style['stroke'] = get_colors(('blue', 800), palette=palette)
        self.box_style['fill'] = get_colors(('blue', 400), palette=palette)

        self.text_style['stroke'] = get_colors(('black', 500), palette=palette)
        self.text_style['fill'] = get_colors(('black', 500), palette=palette)

        return

sort_index += 1
class I2CSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'I2C'
        self.description = 'I2C'

        self.box_style['stroke'] = '#00B8CC',
        self.box_style['fill'] = '#88EBF7'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class SpiSignalFunction(DxSignalFunction):
    index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'SPI'
        self.description = 'SPI'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = '#8CEEBA'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class AdcSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'ADC'
        self.description = 'ADC'

        self.box_style['stroke'] = '#0060CD'
        self.box_style['fill'] = '#A2CEFF'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return


sort_index += 1
class ComparatorSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'Comparator'
        self.description = 'Comparator'

        self.box_style['stroke'] = '#0060CD'
        self.box_style['fill'] = '#A2CEFF'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

    @property
    def text(self):
        name = self.signal.function
        if '_ALT' in name:
            is_alt = True
            name = name.replace('_ALT','')

        if self.signal.group == 'N':
            name = name + '-'
        elif self.signal.group == 'P':
            name = name + '+'
            
        return name

sort_index += 1
class DacSignalFunction(DxSignalFunction):
    type_index = sort_index

    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'DAC'
        self.description = 'DAC'

        self.box_style['stroke'] = '#0060CD'
        self.box_style['fill'] = '#A2CEFF'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class ZcdSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'ZCD'
        self.description = 'ZeroCrossingDetector'

        self.box_style['stroke'] = '#0060CD'
        self.box_style['fill'] = '#A2CEFF'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class SystemSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'System'
        self.description = 'System'

        self.box_style['stroke'] = '#CCAA00'
        self.box_style['fill'] = '#FFE97C'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class OtherSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'OTHER'
        self.description = 'OTHER'

        self.box_style['stroke'] = get_colors(('sunflower', 500), palette=palette)
        self.box_style['fill'] = get_colors(('sunflower', 500), palette=palette)

        self.text_style['stroke'] = get_colors(('black', 500), palette=palette)
        self.text_style['fill'] = get_colors(('black', 500), palette=palette)

        return

sort_index += 1
class ClockSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'Clock'
        self.description = 'Clock'

        self.box_style['stroke'] = '#CCAA00'
        self.box_style['fill'] = '#FFE97C'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class PwmSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'PWM'
        self.description = 'PWM'

        self.box_style['stroke'] = get_colors(('purple', 700), palette=palette)
        self.box_style['fill'] = get_colors(('purple', 500), palette=palette)

        self.text_style['stroke'] = get_colors(('white', 200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return

    @property
    def text(self):
        instance = ''
        if self.instance > 0:
            instance = self.instance

        text = '{}{}.{}'.format(self.name, instance, self.signal.group)

        if self.is_alt:
            text += '/{}'.format(self.alt_position)

        return text


sort_index += 1
class TcaSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'TCA'
        self.description = 'TCA0'

        self.box_style['stroke'] = '#00CCA0'
        self.box_style['fill'] = '#99FFE9'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

    @property
    def text(self):
        instance = ''
        if self.instance > 0:
            instance = self.instance

        text = '{}{}.{}{}'.format(self.name, instance, self.signal.group, self.signal.index)

        if self.is_alt:
            text += '/{}'.format(self.alt_position)

        return text
    
sort_index += 1
class TcbSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'TCB'
        self.description = 'TCBn'

        self.box_style['stroke'] = '#69CC00'
        self.box_style['fill'] = '#DAFFB3'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

    @property
    def text(self):
        text = '{}{}'.format(self.name, self.instance)
        if self.is_alt:
            text += '/{}'.format(self.alt_position)

        return text
    
sort_index += 1
class TcdSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'TCD'
        self.description = 'TCD0'

        self.box_style['stroke'] = '#69CC00'
        self.box_style['fill'] = '#DAFFB3'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

    @property
    def text(self):
        instance = ''
        if self.instance > 0:
            instance = self.instance

        text = '{}{}.{}'.format(self.name, instance, self.signal.group)
            
        if self.is_alt:
            text += '/{}'.format(self.alt_position)
        
        return text
    
sort_index += 1
class LogicSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'LOGIC'
        self.description = 'Logic System'

        self.box_style['stroke'] = get_colors(('belize-hole',700), palette=palette)
        self.box_style['fill'] = get_colors(('belize-hole',600), palette=palette)

        self.text_style['stroke'] = get_colors(('white',200), palette=palette)
        self.text_style['fill'] = get_colors(('white', 200), palette=palette)

        return

    @property
    def text(self):
        group = self.signal.group
        if group == 'EVOUT':
            text = 'EV.OUT'
            index =  self.signal.index # self.pad_name
        elif '_OUT' in group:
            text = group.replace('_OUT', '.OUT')
            index = self.signal.index
        elif '_IN' in group:
            text = group.replace('_IN', '.IN')
            index = self.signal.index
        else:
            text = group
            index = 'x'
            
        return '{}{}'.format(text, index)
    
sort_index += 1
class EvsysSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'EVENT'
        self.description = 'Events'

        self.box_style['stroke'] = '#9600CC'
        self.box_style['fill'] = '#E399FF'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class CclSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'CCL'
        self.description = 'Logic Table'

        self.box_style['stroke'] = '#9600CC'
        self.box_style['fill'] = '#E399FF'

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

sort_index += 1
class ControlSignalFunction(DxSignalFunction):
    type_index = sort_index
    
    def __init__(self, signal):
        super().__init__(signal)

        self.title = 'CLOCK'
        self.description = 'Clock System'

        self.box_style['stroke'] = get_colors(('sunflower', 500), palette=palette)
        self.box_style['fill'] = get_colors(('sunflower', 500), palette=palette)

        self.text_style['stroke'] = 'black'
        self.text_style['fill'] = 'black'

        return

    @property
    def text(self):
        text = self.signal.group
        text = text.replace('XTAL', 'XTL')
        
        return text
    
sort_index += 1
class SkipSignalFunction(DxSignalFunction):
    type_index = sort_index

    def __init__(self, signal):
        super().__init__(signal)

        self.skip = True
        return

sort_index += 1
class SpacerSignalFunction(DxSignalFunction):
    type_index = sort_index

    def __init__(self, signal):
        super().__init__(signal)

        skip = False
        return

