import time
import json
import snapchat_dlp  # https://pypi.org/project/snapchat-dlp/

# from vidstab import VidStab, layer_overlay #https://pypi.org/project/vidstab/
import instaloader  # https://instaloader.github.io/as-module.html

from colorizeOutput import ColorizeOutput


profileList = json.load(open("Profiles.json", "r"))
loginList = json.load(open("myLoginInfo.json", "r"))

DownloadFolerPrefix = "Output"

# TODO Create a way to collect TODO's written inside files into README.MD


def snapchatDownload(personName, SnapchatProfile):
    try:
        snapper = snapchat_dlp.SnapchatDL(
            max_workers=1,
            directory_prefix=f"{DownloadFolerPrefix}/{personName}/{SnapchatProfile}/Snapchat",
        )

        snapper.download(username=SnapchatProfile)
    except KeyError as e:
        pass


def instagramDownload(currentProfile, personName):
    def createInstagramSession():
        return instaloader.Instaloader()
        # return instaloader.Instaloader(
        #             dirname_pattern=dirname_pattern_default
        #         )

    def createInstagramObject(InstaGrabber):
        try:
            previousDir = InstaGrabber.dirname_pattern
            InstaProfileOBJ = instaloader.Profile.from_username(
                InstaGrabber.context, InstaProfile
            )
            return InstaProfileOBJ, InstaGrabber
        except instaloader.exceptions.LoginRequiredException as e:
            waittime = 60
            ColorizeOutput.WARNING(f"Got Login screen. Waiting {waittime} seconds.")
            time.sleep(waittime)
            InstaGrabber = createInstagramSession()
            InstaGrabber.dirname_pattern = previousDir
            createInstagramObject(InstaGrabber)

    try:
        dirname_pattern_default = (
            f"{DownloadFolerPrefix}/{personName}/{currentProfile}/Instagram"
        )
        # Get Instagram Posts from public profiles
        InstaProfile = currentProfile

        InstaGrabber = createInstagramSession()
        InstaGrabber.dirname_pattern = dirname_pattern_default

        if "Instagram" not in AccountBanned:
            # TODO Create support for multiple Useraccounts logins.
            InstagramLoginUser = loginList["Instagram"]["User"]
            InstaGrabber.login(
                InstagramLoginUser, loginList["Instagram"]["Password"]
            )
            InstaDownloadSettingsForLoop = [
                ("highlights", True),
                ("stories", True),
                ("posts", True),
                ("profile_pic", True),
                ("tagged", True),
                ("igtv", True),
            ]
        else:  # If account is banned, only get public info
            print("\n \033[93m Your Instagram user {InstagramLoginUser} has been banned or blocked! \033[0m " * 3)
            InstaDownloadSettingsForLoop = [
                ("posts", True),
                ("profile_pic", True),
                ("tagged", True),
            ]

        # Create Object with type Profile
        InstaProfileOBJ, InstaGrabber = createInstagramObject(InstaGrabber)

        for settings in InstaDownloadSettingsForLoop:
            param_name, param_value = settings
            params = {
                "highlights": False,
                "stories": False,
                "posts": False,
                "profile_pic": False,
                "tagged": False,
                "igtv": False,
                "fast_update": True,
                "post_filter": None,
                "storyitem_filter": None,
                "raise_errors": False,
                "latest_stamps": None,
            }
            params[param_name] = param_value

            if param_name == "highlights" and param_value:
                highlight_list = list(InstaGrabber.get_highlights(InstaProfileOBJ))
                for highlight in highlight_list:
                    folder_name = f"{highlight.title}"
                    InstaGrabber.dirname_pattern = (
                        f"{dirname_pattern_default}/highlights/{folder_name}"
                    )
                    InstaGrabber.download_highlights(
                        InstaProfileOBJ,
                        fast_update=True,
                        filename_target=None,
                        storyitem_filter=None,
                    )
            else:
                InstaGrabber.dirname_pattern = f"{dirname_pattern_default}/{param_name}"
                InstaGrabber.download_profiles([InstaProfileOBJ], **params)
                InstaGrabber.dirname_pattern = dirname_pattern_default

    except instaloader.QueryReturnedBadRequestException as e:
        AccountBanned.append("Instagram")
        instagramDownload(currentProfile, personName)
    except instaloader.exceptions.ConnectionException as e:
        AccountBanned.append("Instagram")
        instagramDownload(currentProfile, personName)


AccountBanned = []
while True:
    # TODO add VSCO support, tise.com too?
    for profile in profileList:
        try:
            if profileList[profile]["Snapchat"]:
                for currentProfileFromFile in profileList[profile]["Snapchat"]:
                    snapchatDownload(
                        SnapchatProfile=currentProfileFromFile, personName=profile
                    )
        except KeyError as e:
            pass
        try:
            if profileList[profile]["Instagram"]:
                for currentProfileFromFile in profileList[profile]["Instagram"]:
                    instagramDownload(
                        currentProfile=currentProfileFromFile, personName=profile
                    )
        except KeyError as e:
            pass

    print()
