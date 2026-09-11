import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from collectors import windows_info

print('get_motherboard_detail:')
print(windows_info.get_motherboard_detail())

print('\nget_bios_detailed_info:')
print(windows_info.get_bios_detailed_info())

print('\nget_chipset_detail:')
print(windows_info.get_chipset_detail())
