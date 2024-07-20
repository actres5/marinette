# Installation

This page (hopefully!) will help you to install Marinette




## Prerequisites

-   [Python](https://www.python.org/)
-   Very basic technical skills
-   A bit of time and patience




## Step-by-step guide

Here is step-by-step guide on how to perform the minimal installation of Marinette:

1.  Download the source code ([marinette-main.zip](https://github.com/actres5/marinette/archive/refs/heads/main.zip))
2.  Unpack it anywhere on your computer
3.  Enter **marinette-main** which you've unpacked in prefered terminal emulator
4.  Generate a preinstall script by running the following:
    -   On Windows: `py scripts\install_marinette.py`
    -   On *nix: `python scripts/install_marinette.py`
5.  Generate a password and an identificator by running the following:
    -   On Windows:
        -   `py scripts\config_password.py MAKE_UP_A_PASSWORD`
        -   `py scripts\config_identificator.py`
    -   On *nix:
        -   `python scripts/config_password.py MAKE_UP_A_PASSWORD`
        -   `python scripts/config_identificator.py`
6.  Copy the script you've generated on step **4** into the game, compile and launch it
    -   The made script is located in **scriptsgh/install_marinette.src**
7.  Copy-paste every **.src** file located in **marinette-main** on your computer to the in-game **/home/guest/Sources/Marinette**
8.  Open **/home/guest/Sources/Marinette/src/marinette.src** and change **password** and **identificator** to the ones you've generated on step 5
9.  Compile and launch **marinette.src**
    -   You can launch Marinette two ways:
        -   With specifying password: `marinette --password PASSWORD_FROM_STEP_5`
        -   Without specifying password. In this case, Marinette will ask you to enter it: `marinette`

Congratulations! You've successfully installed Marinette!

If you want to use Marinette at her best, consider going through [configuration](/catalog/04-configuration.md)
