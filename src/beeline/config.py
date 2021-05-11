from aqt import mw


def get(key):
    config = mw.addonManager.getConfig(__name__)
    try:
        return config[key]
    except KeyError:
        return None
