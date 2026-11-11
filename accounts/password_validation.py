"""Django parol validatorlari, xabarlari o'zbekchada.

Django'ning o'zbekcha tarjimasida bu xabarlar yo'q, shuning uchun shu yerda yozilgan.
"""
from django.contrib.auth import password_validation as base


class UserAttributeSimilarityValidator(base.UserAttributeSimilarityValidator):
    def get_error_message(self):
        return "Parol username, ism yoki familiyangizga juda o'xshash."

    def get_help_text(self):
        return "Parol shaxsiy ma'lumotlaringizga o'xshamasligi kerak."


class MinimumLengthValidator(base.MinimumLengthValidator):
    def get_error_message(self):
        return f"Parol juda qisqa. Kamida {self.min_length} ta belgi bo'lishi kerak."

    def get_help_text(self):
        return f"Parol kamida {self.min_length} ta belgidan iborat bo'lishi kerak."


class CommonPasswordValidator(base.CommonPasswordValidator):
    def get_error_message(self):
        return "Bu parol juda oddiy, uni topish oson."

    def get_help_text(self):
        return "Parol ko'p ishlatiladigan oddiy parol bo'lmasligi kerak."


class NumericPasswordValidator(base.NumericPasswordValidator):
    def get_error_message(self):
        return "Parol faqat raqamlardan iborat bo'lmasligi kerak."

    def get_help_text(self):
        return "Parol faqat raqamlardan iborat bo'lmasligi kerak."
