import i18n
import path_editor


def translate(locale, key):
    i18n.load_path.append('backend/translations')
    i18n.set('locale', locale)
    return  i18n.t(f"foo.{key}")
