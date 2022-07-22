from subprocess import run
from typing import List, Tuple, Dict

from util import echoexit, dbg

def show_menu(
		options: List[str],
		prompt: str = 'mullvad',
		message: str = None,
		allow_custom: bool = False,
		format: str = 's',
		additional_args: List[str] = [],
	) -> Tuple[int, str]:
		parameters = [
			'rofi',
			'-dmenu',
			'-markup-rows',
			'-i',
			'-no-show-icons',
			'-p', prompt,
			'-format', format,
			'-kb-custom-1', 'Control+Return',
			'-kb-accept-custom', 'Alt+1',
			*additional_args
		]

		if message:
			parameters.extend(['-mesg', message.strip()])
		if not allow_custom:
			parameters.extend(['-no-custom'])

		rofi = run(
			parameters,
			input='\n'.join(options),
			capture_output=True,
			encoding='utf-8'
		)

		try:
			result = rofi.stdout
			if format in 'di':
				result = int(result)
			else:
				result = result.strip()
		except Exception as e:
			echoexit('Invalid response.')

		return rofi.returncode, result
