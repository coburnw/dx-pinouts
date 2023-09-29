import microchip_dfp as Dfpack
import pinoutOverview as Overview

import dx_functions


class DxPackageData(Overview.PackageData):
    def __init__(self, package_name, pin_spacing, appdata):
        """

        Args:
            package_name (str): Name of the package shape: 'qfp', 'qfn', 'sop'
            pin_spacing (int): space between adjacent pins in pixels.
            appdata (dict): dictionary of user data to include in package
        """
        package_map = dict(spdip='sop', soic='sop', ssop='sop', tqfp='qfp', vqfn='qfn')

        # shape, sep, count = package_name.partition('-')
        shape = package_name.lower().rstrip('0123456789')
        pin_count = int(package_name.lower().removeprefix(shape))

        if shape in ['sop', 'qfp', 'qfn']:
            pass
        elif shape in package_map:
            shape = package_map[shape]
        else:
            print('unrecognized package shape: {}'.format(shape))
            raise

        super().__init__(shape, pin_count, pin_spacing)

        self.text1 = appdata['text1']
        self.text2 = appdata['text2']

        return


class DxPinmap(Overview.Pinmap):
    def __init__(self, pinmap):
        super().__init__()

        self.reverse_map = dict()
        for mapping in pinmap:
            self.reverse_map[mapping.pad] = int(mapping.position)

            function_label = dx_functions.PinFunctionFactory(mapping.pad)
            pad = Overview.Pad(function_label)
            self.data[int(mapping.position)] = pad

        return

    def get_pad_by_name(self, pad_name):
        return self.data[self.reverse_map[pad_name]]

    def get_pad_by_position(self, index):
        return self.data[int(index)]

    def append_module(self, module):
        """
        :param module: atdf module object
        """

        for name, instance in module.instances.items():
            if not instance.signals:
                continue

            for signal in instance.signals:
                function = dx_functions.SignalFunctionFactory(signal=signal)
                self.get_pad_by_name(signal.pad).append(function)

        return



if __name__ == '__main__':
    import os
    import drawsvg as dw

    x_max = 2000
    y_max = 2000
    dw_page = dw.Drawing(x_max, y_max, origin='center', displayInline=True)
    dw_page.embed_google_font("Roboto Mono")

    # svg coordinates: +x to the right, +y to the bottom
    x_direction = -1  # +1 right, -1 left
    y_direction = 1   # +1 down
    x = -600 * x_direction
    y = -400 * y_direction
    
    dw_page.append(dw.Line(x_max,y, -x_max,y, stroke='black'))
    dw_page.append(dw.Line(x,y_max, x,-y_max, stroke='red'))

    ###

    atdf_path = os.path.expanduser('~/dev/svg/avr-atpack/Microchip.AVR-Dx_DFP.2.3.272/atdf/AVR32DB32.atdf')
    atdf = Dfpack.Atdf(atdf_path)

    for device in atdf.devices:
        print(device.name, device.architecture)

    # variant should be an object containing its pinout, device, and modules.
    for variant in atdf.variants:
        print(variant.ordercode, variant.package)

    variant = atdf.variants[0]
    map = atdf.pinouts[variant.pinout]

    device = atdf.devices[0]
    pinmap = DxPinmap(map)
    for module in device.peripherals:
        pinmap.append_module(module)

    pinmap.sort()
    # split_functions = Overview.Functions()
    # split_functions.append(dx_functions.PwmSignalFunction(None))
    # pinmap.split(split_functions)

    appdata = dict(
        text1 = device.name,
        text2 = variant.package
    )

    package_data = DxPackageData(variant.package, pinmap.spacing, appdata)
    package_shape = package_data.shape
    package = Overview.Package(package_shape, package_data)

    layout = 'orthogonal'
    pinout = Overview.Pinout(layout, pinmap, package)
    dw_page.append(pinout(x=0, y=-200))

    legend = Overview.Legend(pinmap)
    dw_page.append(legend(x=pinout.x+500, y=pinout.y+500))

    dw_page.save_svg('junk.svg')
