# from genericpath import isfile
import time
import json
import os
import argparse
import sys
import snapchat_dlp  # https://pypi.org/project/snapchat-dlp/

import vscodl # https://pypi.org/project/vsco-dl/

# from vidstab import VidStab, layer_overlay #https://pypi.org/project/vidstab/
import instaloader  # https://instaloader.github.io/as-module.html

from colorizeOutput import ColorizeOutput


profileList = json.load(open("Profiles.json", "r"))
loginList = json.load(open("myLoginInfo.json", "r"))

DownloadFolerPrefix = "./Output"
InstaDownloadSettingsForLoop = {}
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


def instagramDownload(currentProfile, personName, mode, resyncDownloads):
    def createInstagramSession():
        return instaloader.Instaloader()
        # return instaloader.Instaloader(
        #             dirname_pattern=dirname_pattern_default
        #         )

    def fetch_instagram_login():
        # TODO Create support for multiple Useraccounts logins.
        for user in loginList["Instagram"]:
            if user["Banned"] == False:
                return user

        return None

    def createInstagramObject(InstaGrabber, triesLeft=1):
        if int(triesLeft) <= 0:
            return
        try:
            previousDir = InstaGrabber.dirname_pattern
            InstaProfileOBJ = instaloader.Profile.from_username(
                InstaGrabber.context, InstaProfile
            )
            return InstaProfileOBJ, InstaGrabber
        except instaloader.exceptions.LoginRequiredException as e:
            waittime = 1
            ColorizeOutput.WARNING(f"Got Login screen. Waiting {waittime} seconds.")
            time.sleep(waittime)
            InstaGrabber = createInstagramSession()
            InstaGrabber.dirname_pattern = previousDir
            createInstagramObject(InstaGrabber, triesLeft=triesLeft - 1)

    def updateDownloadSettings(settingsToUpdate):
        for key, value in settingsToUpdate:
            InstaDownloadSettingsForLoop[key] = value
        return InstaDownloadSettingsForLoop

    def resync_profiles(profile):
        """
        Add profiles that has been synced to a list.
        """

        # TODO NEXT IDEA: Legg til "last full copy eller lignende i profile.json. Det innebærer å konvertere listene over profiler til egene Keys, men det burte la seg gjøre."
        reync_filename = "resync_status"
        if not os.isfile(reync_filename):
            with open(reync_filename, "w+") as file:
                file.write()

        def read():
            """
            Returns a string with profiles that has been synced already.
            """
            with open(reync_filename, "r") as file:
                return str(file.read())

        def write(ThingToWrite):
            with open(reync_filename, "w") as file:
                resync_list = file.read()
                resync_list = resync_list + f"\n{ThingToWrite}"

        def clear():
            with open(reync_filename, "w+") as file:
                file.write()

    dirname_pattern_default = (
        f"{DownloadFolerPrefix}/{personName}/{currentProfile}/Instagram"
    )

    only_public_profiles = False

    # Get Instagram Posts from public profiles
    InstaProfile = currentProfile

    InstaGrabber = createInstagramSession()
    InstaGrabber.dirname_pattern = dirname_pattern_default

    InstaDownloadSettingsForLoop = {
        "highlights": False,
        "stories": False,
        "posts": False,
        "profile_pic": False,
        "tagged": False,
        "igtv": False,
        "fast_update": {True if resyncDownloads else False},
        "post_filter": None,
        "storyitem_filter": None,
        "raise_errors": False,
        "latest_stamps": None,
    }

    # If -InstagramLogin is parsed:
    if mode == "logged_in":
        instagram_login = fetch_instagram_login()
        if instagram_login is not None:
            # InstagramLoginUser = fetch_instagram_login()
            try:
                InstaGrabber.login(instagram_login["User"], instagram_login["Password"])
                InstaDownloadSettingsForLoop = updateDownloadSettings(
                    [
                        ("stories", True),
                        ("posts", True),
                        ("profile_pic", True),
                        ("tagged", True),
                        ("igtv", True),
                    ]
                )
                # ("highlights", True),
            except instaloader.exceptions.ConnectionException as e:
                ColorizeOutput.WARNING(
                    "An Error occurred when logging in to Instagram. This could be a scraper response from Instagram, or a wrong password."
                )
                print(e)
    else:
        # If -InstagramPublic is parsed
        only_public_profiles = True
        print(f"\n \033[93m Downloading public information only. \033[0m ")
        InstaDownloadSettingsForLoop = updateDownloadSettings(
            [
                ("posts", True),
                ("profile_pic", True),
                ("tagged", True),
            ]
        )

    # Create Object with type Profile
    try:
        InstaProfileOBJ, InstaGrabber = createInstagramObject(InstaGrabber)
    except TypeError as e:
        return
    try:
        for settings in InstaDownloadSettingsForLoop:
            param_name = settings
            param_value = InstaDownloadSettingsForLoop[settings]
            params = {
                "highlights": False,
                "stories": False,
                "posts": False,
                "profile_pic": False,
                "tagged": False,
                "igtv": False,
                "fast_update": {True if resyncDownloads else False},
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
    except instaloader.LoginRequiredException as e:
        if only_public_profiles:
            pass
        else:
            raise e
    # except instaloader.QueryReturnedBadRequestException as e:
    #     banned_accounts.append("Instagram")
    #     instagramDownload(currentProfile, personName, mode)
    # except instaloader.exceptions.ConnectionException as e:
    #     banned_accounts.append("Instagram")
    #     instagramDownload(currentProfile, personName)


def vscoDownload(vscoProfile, personName):

    # outputPath = os.path.abspath(os.path.join(DownloadFolerPrefix,personName,vscoProfile, 'VSCO'))
    outputPath = f"{DownloadFolerPrefix}/{personName}/{vscoProfile}/VSCO"
    vscoDownloader = vscodl.Scraper(username=vscoProfile,  output_dir=outputPath)
    # vscoDownloader = vscodl()
    vscoDownloader.download_images()





def download_instagram_profiles(profile_list, mode, resyncDownloads):
    repeat_downloads_wait_time_instagram = repeat_downloads_wait_time /2
    for profile, details in profile_list.items():
        try:
            ColorizeOutput.OKGREEN(
                f"Downloading Instagram profiles with logged in user. \nCurrent Instagram Profile: {profile}"
            )
            for current_profile in details["Instagram"]:
                instagramDownload(
                    currentProfile=current_profile,
                    personName=profile,
                    mode=mode,
                    resyncDownloads=resyncDownloads,
                )
            ColorizeOutput.WARNING(f"\nWaiting {repeat_downloads_wait_time_instagram} seconds before repeating. This is needed for the instagram rate limiter.")
            time.sleep(repeat_downloads_wait_time)
        except KeyError:
            pass


def download_snapchat_profiles(profile_list):
    for profile, details in profile_list.items():
        try:
            for current_profile in details["Snapchat"]:
                snapchatDownload(SnapchatProfile=current_profile, personName=profile)
        except KeyError:
            pass

def download_vsco_profiles(profile_list):
    for profile, details in profile_list.items():
        try:
            for current_profile in details["VSCO"]:
                os.chdir(working_dir)
                vscoDownload(vscoProfile=current_profile, personName=profile)
        except KeyError:
            pass


def main():
    repeat_downloads = False
    resyncDownloads = False
    repeat_downloads_wait_time = 60
    parser = argparse.ArgumentParser(
        description="Download profiles from Instagram and Snapchat."
    )
    parser.add_argument(
        "-S", action="store_true", help="Download Snapchat profiles from public users"
    )
    parser.add_argument(
        "-I",
        action="store_true",
        help="Download Instagram profiles, must be used together with -ip or -ilogin",
    )
    parser.add_argument(
        "-ip",
        action="store_true",
        help="Download Instagram profiles with a public user",
    )
    parser.add_argument(
        "-ilogin",
        action="store_true",
        help="Download Instagram profiles with a logged-in user",
    )
    parser.add_argument(
        "-iresync",
        action="store_true",
        help="Deactivate fast_update. Do not about current download even if download already exists.",
    )
    parser.add_argument(
        "-r",
        type=int,
        nargs="?",
        const=-1,
        help="Repeat the script. Do '-r int' to set the number of times it shall repeat.",
    )
    parser.add_argument(
        "-t",
        type=int,
        nargs="?",
        const=repeat_downloads_wait_time,
        help="Used with -r to set a waittime for the repeat. Default is 60 seconds",
    )
    parser.add_argument(
        "-vsco",
        action="store_true",
        help="Download VSCO profiles with a public user",
    )
    args = parser.parse_args()

    if args.I and not (args.ip or args.ilogin) and not args.S:
        print("You need to pass either -ip or -ilogin to run Instagram download")
        sys.exit(1)

    if args.iresync:
        resyncDownloads = True

    if args.r:
        repeat_downloads = True

    if args.t:
        repeat_downloads_wait_time = args.t

    instagram_mode = "public" if args.ip else "logged_in"

    if args.I:
        download_instagram_profiles(profileList, instagram_mode, resyncDownloads)
    if args.S:
        download_snapchat_profiles(profileList)
    if args.vsco:
        download_vsco_profiles(profileList)

    if repeat_downloads:
        print(f"\nWaiting {repeat_downloads_wait_time} before repeating")
        time.sleep(repeat_downloads_wait_time)
        main()

working_dir = None
if working_dir == None:
    working_dir = os.getcwd()
os.chdir(working_dir)
if __name__ == "__main__":
    main()


# banned_accounts = []
# while True:
#     # TODO add VSCO support, tise.com too?
#     for profile in profileList:
#         try:
#             if profileList[profile]["Instagram"]:
#                 for currentProfileFromFile in profileList[profile]["Instagram"]:
#                     instagramDownload(
#                         currentProfile=currentProfileFromFile, personName=profile
#                     )
#         except KeyError as e:
#             pass
#         try:
#             if profileList[profile]["Snapchat"]:
#                 for currentProfileFromFile in profileList[profile]["Snapchat"]:
#                     snapchatDownload(
#                         SnapchatProfile=currentProfileFromFile, personName=profile
#                     )
#         except KeyError as e:
#             pass
