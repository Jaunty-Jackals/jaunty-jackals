# Jaunty Jackals 2021 Summer Code Jam Repository

<div style="text-align: center;">

![logo+big](bin/utils/graphics/jackal_logo_big.png)

</div>

Work in progress!

## Requirements

- Python 3.9.5+
- pulseaudio-utils
- Functional speakers

## Setting up & Running the App

### 1. Clone the repository

```sh
git clone https://github.com/Jaunty-Jackals/jaunty-jackals.git
```

\* *The repository address provided above may change once Python discord as accepted our submission into their archive of Code Jam repositories.*

### 2. Install requirements

#### Windows <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Windows_logo_-_2021.svg/1920px-Windows_logo_-_2021.svg.png" width="16">

```sh
# Change directory to project root directory
C:~\> cd jaunty-jackals

# Set up virtual environment
C:~\jaunty-jackals\> python -m venv venv

# Enter virtual environment
C:~\jaunty-jackals\> .\venv\Scripts\activate

# Install requirements
(venv) C:~\jaunty-jackals\> pip install -r requirements/windows.txt
```

#### macOS <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Apple_Computer_Logo_rainbow.svg" width="16">

```sh
# Change directory to project root directory
$ cd jaunty-jackals

# Set up virtual environment
$ python -m venv venv

# Enter virtual environment
$ source venv/bin/activate

# Install requirements
(venv) $ pip install -r requirements/macos.txt
```

#### Linux <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Tux_Classic_flat_look_3D.svg/1920px-Tux_Classic_flat_look_3D.svg.png" width="16">

```sh
# Change directory to project root directory
$ cd jaunty-jackals

# Set up virtual environment
$ python -m venv venv

# Enter virtual environment
$ source venv/bin/activate

# Install the requirements
(venv) $ python -m pip install -r requirements/dev-requirements.txt
```

### 3. Run the app

**macOS** <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Apple_Computer_Logo_rainbow.svg" width="16"> & **Linux** <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Tux_Classic_flat_look_3D.svg/1920px-Tux_Classic_flat_look_3D.svg.png" width="16">

```sh
(venv) $ python bin/demo.py
```

**Windows** <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Windows_logo_-_2021.svg/1920px-Windows_logo_-_2021.svg.png" width="16">

```sh
(venv) C:~\jaunty-jackals\> python bin/demo.py
```

## Team Members

| Member | OS | Roles |
| :---: | :---: | :--- |
| [ponte-vecchio (Lead)](https://github.com/ponte-vecchio) | <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Apple_Computer_Logo_rainbow.svg" width="24"><img src="https://archlinux.org/logos/archlinux-icon-crystal-64.svg" width="24"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Openlogo-debianV2.svg/1654px-Openlogo-debianV2.svg.png" width="24"> | Repository management, menu, UI/UX & colours |
| [NoblySP](https://github.com/NoblySP) |<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Windows_logo_-_2021.svg/1920px-Windows_logo_-_2021.svg.png" width="24">| Battleship|
| [vguo2037](https://github.com/vguo2037) |<img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Apple_Computer_Logo_rainbow.svg" width="24">| ConnectFour |
| [aphkyle](https://github.com/aphkyle) |<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Windows_logo_-_2021.svg/1920px-Windows_logo_-_2021.svg.png" width="24">| Snake |
| [sapgan](https://github.com/sapgan) |<img src="https://upload.wikimedia.org/wikipedia/commons/4/4b/Kali_Linux_2.0_wordmark.svg" height="24">| Minesweeper |
| [edwin10151](https://github.com/edwin10151) |<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Windows_logo_-_2021.svg/1920px-Windows_logo_-_2021.svg.png" width="24">| 2048 |

## Asset Credits

- Shane Iveson (Logo)
- Juhani Junkala (Menu sound effects)
- BoxCat Games (Menu music)
- dpren ([In-game music](https://freesound.org/people/dpren/sounds/320685/), CC BY 3.0 License)
- Tissman (In-game sfx [1](https://freesound.org/people/Tissman/sounds/534815/) & [2](https://freesound.org/people/Tissman/sounds/534823/), CC0 1.0 License)
- F.M.Audio ([In-game sfx](https://freesound.org/people/F.M.Audio/sounds/557141/), CC BY 3.0 License)
- gamer127 ([In-game sfx](https://freesound.org/people/gamer127/sounds/457547/), CC0 1.0 License)
- Lightning Editor ([In-game sfx](https://www.youtube.com/watch?v=HTXiJpCDiH4), CC BY License)
- Free Sounds Library ([In-game sfx](https://www.youtube.com/watch?v=DroVubuGaGk), CC BY License)
