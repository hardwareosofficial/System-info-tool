import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from collectors import linux_info, macos_info

print('linux get_motherboard_detail:')
print(linux_info.get_motherboard_detail())
print('\nlinux get_chipset_hint:')
print(linux_info.get_chipset_hint())

print('\nmacos get_motherboard_detail:')
print(macos_info.get_motherboard_detail())
print('\nmacos get_chipset_hint:')
print(macos_info.get_chipset_hint())
