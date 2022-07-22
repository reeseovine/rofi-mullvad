# rofi-mullvad

## Usage

1. Have these programs installed:  
  - python 3  
  - mullvad-cli  
  - rofi  
  <!-- - libnotify (for notifications) -->
2. Run `main.py`

### Configuration

Near the top of `main.py` there are 2 values you can modify: `LATITUDE` and `LONGITUDE`. Use these to set your location so that auto connect will work.


## Project status

- [x] Parse locations from `mullvad relay list`
  - [x] Countries
  - [x] Cities
  - [ ] Servers
- [x] Find closest city by geo coords
- [x] Rofi interface
  - [ ] Wofi support
- [ ] libnotify interface
- [x] Connection menu
- [x] Settings menu
- [x] `mullvad-exclude` drun wrapper
- [ ] Status bar function

### Planned menu structure

- Connect
  - Auto
  - [all country names]
    ctrl+enter
    - [city names]
      ctrl+enter
      - [server names]
- Disconnect (show if connected)
- Reconnect (show if connected)
- Launch program with `mullvad-exclude` (show if connected)
- Settings
  - Account
  - Auto connect
  - Beta notifications
  - Custom DNS
  - Kill switch
  - LAN access
  - Obfuscation
  - Relay constraints
