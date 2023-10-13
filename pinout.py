# pinout.py - Application. reads a json config file of variants and builds an SVG visual datasheet.
#
# Copyright (c) 2023 Coburn Wightman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json

import microchip_dfp as Dfpack
import pinoutOverview as Overview

from page import Page
import dx_functions


class DxPackage(Overview.Package):
    def __init__(self, package_name, appdata):
        """

        Args:
            variant_package:

        Returns:
            package_name (str): Name of the variant package such as 'tqfp32', 'vqfn44', 'soic16'
            appdata (dict): dictionary of user data to include in package
        """
        shape, pin_count = self.parse_variant_package(package_name)
        super().__init__(shape, pin_count)

        self.text1 = appdata['text1']
        self.text2 = appdata['text2']

        return

    def parse_variant_package(self, package_name):
        package_map = dict(spdip='sop', soic='sop', ssop='sop', tqfp='qfp', vqfn='qfn')

        # shape, sep, count = package_name.partition('-')
        shape = package_name.lower().rstrip('0123456789')
        pin_count = int(package_name.lower().removeprefix(shape))
        shape = shape.rstrip('-')

        if shape in ['sop', 'qfp', 'qfn']:
            pass
        elif shape in package_map:
            shape = package_map[shape]
        else:
            print('unrecognized package shape: {}'.format(shape))
            raise

        return shape, pin_count

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


class DxPage(Page):
    def __init__(self, family_config, variant_name):
        self.page_config = family_config['page']
        self.variant_config = family_config[variant_name]
        self.variant_name = variant_name

        atdf = self.load_atdf(self.variant_config)
        pinmap = self.build_pinmap(atdf)

        appdata = dict(
            text1=self.variant_config['part_range'],
            text2=self.variant_config['package_range']
        )
        package = DxPackage(self.variant_config['package'], appdata)

        layout = self.variant_config['layout']
        pinout = Overview.Pinout(layout, pinmap, package)
        legend = Overview.Legend(pinmap)

        super().__init__(self.page_config, pinout, legend)
        return

    def save(self, filepath=None):
        if filepath is None:
            filepath = self.variant_name

        super().save(filepath)
        return

    def load_atdf(self, variant_config):
        atdf_home = os.path.expanduser(self.page_config['atdf_home'])
        atdf_name = variant_config['atdf_name']

        atdf_path = '{}/{}'.format(atdf_home, atdf_name)
        atdf = Dfpack.Atdf(atdf_path)

        return atdf

    def build_pinmap(self, atdf):
        variant = atdf.variants[0]

        map = atdf.pinouts[variant.pinout]
        pinmap = DxPinmap(map)

        device = atdf.devices[0]
        for module in device.peripherals:
            pinmap.append_module(module)

        pinmap.sort()
        # split_functions = Overview.Functions()
        # split_functions.append(dx_functions.PwmSignalFunction(None))
        # pinmap.split(split_functions)

        return pinmap

class Pages:
    def __init__(self, config_name):
        self.family_config = self.load(config_name)
        return

    @property
    def page_config(self):
        return self.family_config['page']

    def __iter__(self):
        for key in self.family_config:
            if key.lower() == 'page':
                continue

            yield DxPage(self.family_config, key)

    def load(self, name):
        basename = os.path.basename(name)
        name, suffix = os.path.splitext(basename)

        path = '{}.json'.format(name)
        print('loading config file: {}'.format(path))

        with open(path, 'r') as fp:
            family = json.load(fp)

        return family


if __name__ == '__main__':
    fname = 'da.json'

    pages = Pages(fname)
    for page in pages:
        page.save()

    exit()

