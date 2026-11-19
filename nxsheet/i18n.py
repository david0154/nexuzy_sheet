# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
# Website: https://nexuzy.in
#
# Licensed under the MIT License. See the LICENSE file in the project
# root for the full license text.
# --------------------------------------------------------------------

"""

**Provides**

 * :data:`LANGUAGES`
 * :data:`TRANSLATIONS`
 * :func:`tr`
 * :func:`set_language`
 * :func:`current_language`
 * :func:`language_name`
 * :func:`apply_to`

Nexuzy Sheet ships with nine user interface languages. The translation layer
works on the English source strings that are used when the menus and actions
are created: :func:`apply_to` walks all actions of a window and replaces the
text with the translation of the current language. Actions whose text has no
entry in the catalog keep their English text, so partially translated builds
stay usable.

"""

from PyQt6.QtGui import QAction

#: User interface languages of Nexuzy Sheet in menu order
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "bn": "বাংলা",
    "ta": "தமிழ்",
    "es": "Español",
    "fr": "Français",
    "zh": "中文",
    "ru": "Русский",
    "ja": "日本語",
}

#: Language that is used if no language has been selected yet
DEFAULT_LANGUAGE = "en"

#: Source string -> translated string per language code
TRANSLATIONS = {
    "en": {},
    "hi": {
        "File": "फ़ाइल",
        "Edit": "संपादन",
        "View": "दृश्य",
        "Format": "स्वरूप",
        "Macro": "मैक्रो",
        "Help": "सहायता",
        "Language": "भाषा",
        "Toolbars": "टूलबार",
        "New": "नया",
        "Open": "खोलें",
        "Save": "सहेजें",
        "Save As": "इस रूप में सहेजें",
        "Import": "आयात करें",
        "Export": "निर्यात करें",
        "Print": "प्रिंट करें",
        "Print preview": "प्रिंट पूर्वावलोकन",
        "Preferences": "वरीयताएँ",
        "Quit": "बाहर निकलें",
        "Recent files": "हाल की फ़ाइलें",
        "Auto save": "स्वतः सहेजें",
        "Version history": "संस्करण इतिहास",
        "Undo": "पूर्ववत करें",
        "Redo": "फिर से करें",
        "Cut": "काटें",
        "Copy": "प्रतिलिपि करें",
        "Copy results": "परिणाम प्रतिलिपि करें",
        "Paste": "चिपकाएँ",
        "Paste as": "इस रूप में चिपकाएँ",
        "Find": "खोजें",
        "Find next": "अगला खोजें",
        "Replace": "बदलें",
        "Sort ascending": "आरोही क्रम में क्रमबद्ध करें",
        "Sort descending": "अवरोही क्रम में क्रमबद्ध करें",
        "Fill down": "नीचे भरें",
        "Fill right": "दाएँ भरें",
        "Insert rows": "पंक्तियाँ जोड़ें",
        "Insert columns": "स्तंभ जोड़ें",
        "Delete rows": "पंक्तियाँ हटाएँ",
        "Delete columns": "स्तंभ हटाएँ",
        "Resize grid": "ग्रिड का आकार बदलें",
        "Fullscreen": "पूर्ण स्क्रीन",
        "Dark mode": "गहरा मोड",
        "Zoom in": "ज़ूम इन",
        "Zoom out": "ज़ूम आउट",
        "Go to cell": "कक्ष पर जाएँ",
        "Bold": "मोटा",
        "Italics": "तिरछा",
        "Underline": "रेखांकित",
        "Strikethrough": "स्ट्राइकथ्रू",
        "Merge cells": "कक्ष विलय करें",
        "Freeze cell": "कक्ष स्थिर करें",
        "Lock cell": "कक्ष लॉक करें",
        "Insert image": "छवि डालें",
        "Insert chart": "चार्ट डालें",
        "Insert function": "फ़ंक्शन डालें",
        "Manual": "मैनुअल",
        "Tutorial": "ट्यूटोरियल",
        "Dependencies": "निर्भरताएँ",
        "About Nexuzy Sheet": "Nexuzy Sheet के बारे में",
        "Close": "बंद करें",
        "Cancel": "रद्द करें",
        "OK": "ठीक है",
        "License": "लाइसेंस",
        "Support": "सहायता",
        "Settings": "सेटिंग्स",
        "New from template": "टेम्पलेट से नया",
        "Offline AI model": "ऑफ़लाइन AI मॉडल",
        "AutoFit columns": "स्तंभ स्वतः फ़िट करें",
        "AutoFit rows": "पंक्तियाँ स्वतः फ़िट करें",
        "AutoFit selection": "चयन स्वतः फ़िट करें",
    },
    "bn": {
        "File": "ফাইল",
        "Edit": "সম্পাদনা",
        "View": "দৃশ্য",
        "Format": "বিন্যাস",
        "Macro": "ম্যাক্রো",
        "Help": "সহায়তা",
        "Language": "ভাষা",
        "Toolbars": "টুলবার",
        "New": "নতুন",
        "Open": "খুলুন",
        "Save": "সংরক্ষণ করুন",
        "Save As": "এই নামে সংরক্ষণ",
        "Import": "আমদানি",
        "Export": "রপ্তানি",
        "Print": "মুদ্রণ",
        "Print preview": "মুদ্রণ পূর্বরূপ",
        "Preferences": "পছন্দসমূহ",
        "Quit": "প্রস্থান",
        "Recent files": "সাম্প্রতিক ফাইল",
        "Auto save": "স্বয়ংক্রিয় সংরক্ষণ",
        "Version history": "সংস্করণ ইতিহাস",
        "Undo": "পূর্বাবস্থায় ফেরান",
        "Redo": "পুনরায় করুন",
        "Cut": "কাটুন",
        "Copy": "অনুলিপি",
        "Copy results": "ফলাফল অনুলিপি",
        "Paste": "পেস্ট করুন",
        "Paste as": "এইভাবে পেস্ট করুন",
        "Find": "খুঁজুন",
        "Find next": "পরবর্তী খুঁজুন",
        "Replace": "প্রতিস্থাপন",
        "Sort ascending": "ঊর্ধ্বক্রমে সাজান",
        "Sort descending": "অধঃক্রমে সাজান",
        "Fill down": "নিচে পূরণ করুন",
        "Fill right": "ডানে পূরণ করুন",
        "Insert rows": "সারি যোগ করুন",
        "Insert columns": "কলাম যোগ করুন",
        "Delete rows": "সারি মুছুন",
        "Delete columns": "কলাম মুছুন",
        "Resize grid": "গ্রিডের আকার বদলান",
        "Fullscreen": "পূর্ণ পর্দা",
        "Dark mode": "ডার্ক মোড",
        "Zoom in": "জুম ইন",
        "Zoom out": "জুম আউট",
        "Go to cell": "কক্ষে যান",
        "Bold": "গাঢ়",
        "Italics": "ইটালিক",
        "Underline": "আন্ডারলাইন",
        "Strikethrough": "স্ট্রাইকথ্রু",
        "Merge cells": "কক্ষ একত্রিত করুন",
        "Freeze cell": "কক্ষ স্থির করুন",
        "Lock cell": "কক্ষ লক করুন",
        "Insert image": "ছবি যোগ করুন",
        "Insert chart": "চার্ট যোগ করুন",
        "Insert function": "ফাংশন যোগ করুন",
        "Manual": "ম্যানুয়াল",
        "Tutorial": "টিউটোরিয়াল",
        "Dependencies": "নির্ভরতাসমূহ",
        "About Nexuzy Sheet": "Nexuzy Sheet সম্পর্কে",
        "Close": "বন্ধ করুন",
        "Cancel": "বাতিল",
        "OK": "ঠিক আছে",
        "License": "লাইসেন্স",
        "Support": "সহায়তা",
        "Settings": "সেটিংস",
        "New from template": "টেমপ্লেট থেকে নতুন",
        "Offline AI model": "অফলাইন AI মডেল",
        "AutoFit columns": "কলাম স্বয়ংক্রিয় ফিট",
        "AutoFit rows": "সারি স্বয়ংক্রিয় ফিট",
        "AutoFit selection": "নির্বাচন স্বয়ংক্রিয় ফিট",
    },
    "ta": {
        "File": "கோப்பு",
        "Edit": "தொகுத்தல்",
        "View": "காட்சி",
        "Format": "வடிவம்",
        "Macro": "மேக்ரோ",
        "Help": "உதவி",
        "Language": "மொழி",
        "Toolbars": "கருவிப்பட்டைகள்",
        "New": "புதியது",
        "Open": "திற",
        "Save": "சேமி",
        "Save As": "இவ்வாறு சேமி",
        "Import": "இறக்குமதி",
        "Export": "ஏற்றுமதி",
        "Print": "அச்சிடு",
        "Print preview": "அச்சு முன்னோட்டம்",
        "Preferences": "விருப்பங்கள்",
        "Quit": "வெளியேறு",
        "Recent files": "சமீபத்திய கோப்புகள்",
        "Auto save": "தானியங்கி சேமிப்பு",
        "Version history": "பதிப்பு வரலாறு",
        "Undo": "செயல்தவிர்",
        "Redo": "மீள்செய்",
        "Cut": "வெட்டு",
        "Copy": "நகலெடு",
        "Copy results": "முடிவுகளை நகலெடு",
        "Paste": "ஒட்டு",
        "Paste as": "இவ்வாறு ஒட்டு",
        "Find": "தேடு",
        "Find next": "அடுத்ததைத் தேடு",
        "Replace": "மாற்று",
        "Sort ascending": "ஏறுவரிசையில் வரிசைப்படுத்து",
        "Sort descending": "இறங்குவரிசையில் வரிசைப்படுத்து",
        "Fill down": "கீழே நிரப்பு",
        "Fill right": "வலப்புறம் நிரப்பு",
        "Insert rows": "வரிசைகளைச் செருகு",
        "Insert columns": "நிரல்களைச் செருகு",
        "Delete rows": "வரிசைகளை நீக்கு",
        "Delete columns": "நிரல்களை நீக்கு",
        "Resize grid": "கட்டத்தின் அளவை மாற்று",
        "Fullscreen": "முழுத்திரை",
        "Dark mode": "இருண்ட பயன்முறை",
        "Zoom in": "பெரிதாக்கு",
        "Zoom out": "சிறிதாக்கு",
        "Go to cell": "கலத்திற்குச் செல்",
        "Bold": "தடிமன்",
        "Italics": "சாய்வு",
        "Underline": "அடிக்கோடு",
        "Strikethrough": "கோடு கிழி",
        "Merge cells": "கலங்களை இணை",
        "Freeze cell": "கலத்தை நிலைப்படுத்து",
        "Lock cell": "கலத்தைப் பூட்டு",
        "Insert image": "படத்தைச் செருகு",
        "Insert chart": "வரைபடத்தைச் செருகு",
        "Insert function": "சார்பைச் செருகு",
        "Manual": "கையேடு",
        "Tutorial": "பயிற்சி",
        "Dependencies": "சார்புகள்",
        "About Nexuzy Sheet": "Nexuzy Sheet பற்றி",
        "Close": "மூடு",
        "Cancel": "ரத்து",
        "OK": "சரி",
        "License": "உரிமம்",
        "Support": "ஆதரவு",
        "Settings": "அமைப்புகள்",
        "New from template": "டெம்ப்ளேட்டிலிருந்து புதியது",
        "Offline AI model": "ஆஃப்லைன் AI மாதிரி",
        "AutoFit columns": "நிரல்களை தானாகப் பொருத்து",
        "AutoFit rows": "வரிசைகளை தானாகப் பொருத்து",
        "AutoFit selection": "தேர்வை தானாகப் பொருத்து",
    },
    "es": {
        "File": "Archivo",
        "Edit": "Editar",
        "View": "Ver",
        "Format": "Formato",
        "Macro": "Macro",
        "Help": "Ayuda",
        "Language": "Idioma",
        "Toolbars": "Barras de herramientas",
        "New": "Nuevo",
        "Open": "Abrir",
        "Save": "Guardar",
        "Save As": "Guardar como",
        "Import": "Importar",
        "Export": "Exportar",
        "Print": "Imprimir",
        "Print preview": "Vista previa de impresión",
        "Preferences": "Preferencias",
        "Quit": "Salir",
        "Recent files": "Archivos recientes",
        "Auto save": "Guardado automático",
        "Version history": "Historial de versiones",
        "Undo": "Deshacer",
        "Redo": "Rehacer",
        "Cut": "Cortar",
        "Copy": "Copiar",
        "Copy results": "Copiar resultados",
        "Paste": "Pegar",
        "Paste as": "Pegar como",
        "Find": "Buscar",
        "Find next": "Buscar siguiente",
        "Replace": "Reemplazar",
        "Sort ascending": "Orden ascendente",
        "Sort descending": "Orden descendente",
        "Fill down": "Rellenar hacia abajo",
        "Fill right": "Rellenar a la derecha",
        "Insert rows": "Insertar filas",
        "Insert columns": "Insertar columnas",
        "Delete rows": "Eliminar filas",
        "Delete columns": "Eliminar columnas",
        "Resize grid": "Cambiar tamaño de la cuadrícula",
        "Fullscreen": "Pantalla completa",
        "Dark mode": "Modo oscuro",
        "Zoom in": "Acercar",
        "Zoom out": "Alejar",
        "Go to cell": "Ir a la celda",
        "Bold": "Negrita",
        "Italics": "Cursiva",
        "Underline": "Subrayado",
        "Strikethrough": "Tachado",
        "Merge cells": "Combinar celdas",
        "Freeze cell": "Inmovilizar celda",
        "Lock cell": "Bloquear celda",
        "Insert image": "Insertar imagen",
        "Insert chart": "Insertar gráfico",
        "Insert function": "Insertar función",
        "Manual": "Manual",
        "Tutorial": "Tutorial",
        "Dependencies": "Dependencias",
        "About Nexuzy Sheet": "Acerca de Nexuzy Sheet",
        "Close": "Cerrar",
        "Cancel": "Cancelar",
        "OK": "Aceptar",
        "License": "Licencia",
        "Support": "Soporte",
        "Settings": "Configuración",
        "New from template": "Nuevo desde plantilla",
        "Offline AI model": "Modelo de IA sin conexión",
        "AutoFit columns": "Ajustar columnas automáticamente",
        "AutoFit rows": "Ajustar filas automáticamente",
        "AutoFit selection": "Ajustar selección automáticamente",
    },
    "fr": {
        "File": "Fichier",
        "Edit": "Édition",
        "View": "Affichage",
        "Format": "Format",
        "Macro": "Macro",
        "Help": "Aide",
        "Language": "Langue",
        "Toolbars": "Barres d'outils",
        "New": "Nouveau",
        "Open": "Ouvrir",
        "Save": "Enregistrer",
        "Save As": "Enregistrer sous",
        "Import": "Importer",
        "Export": "Exporter",
        "Print": "Imprimer",
        "Print preview": "Aperçu avant impression",
        "Preferences": "Préférences",
        "Quit": "Quitter",
        "Recent files": "Fichiers récents",
        "Auto save": "Enregistrement automatique",
        "Version history": "Historique des versions",
        "Undo": "Annuler",
        "Redo": "Rétablir",
        "Cut": "Couper",
        "Copy": "Copier",
        "Copy results": "Copier les résultats",
        "Paste": "Coller",
        "Paste as": "Coller comme",
        "Find": "Rechercher",
        "Find next": "Rechercher suivant",
        "Replace": "Remplacer",
        "Sort ascending": "Tri croissant",
        "Sort descending": "Tri décroissant",
        "Fill down": "Remplir vers le bas",
        "Fill right": "Remplir vers la droite",
        "Insert rows": "Insérer des lignes",
        "Insert columns": "Insérer des colonnes",
        "Delete rows": "Supprimer des lignes",
        "Delete columns": "Supprimer des colonnes",
        "Resize grid": "Redimensionner la grille",
        "Fullscreen": "Plein écran",
        "Dark mode": "Mode sombre",
        "Zoom in": "Zoom avant",
        "Zoom out": "Zoom arrière",
        "Go to cell": "Atteindre la cellule",
        "Bold": "Gras",
        "Italics": "Italique",
        "Underline": "Souligné",
        "Strikethrough": "Barré",
        "Merge cells": "Fusionner les cellules",
        "Freeze cell": "Figer la cellule",
        "Lock cell": "Verrouiller la cellule",
        "Insert image": "Insérer une image",
        "Insert chart": "Insérer un graphique",
        "Insert function": "Insérer une fonction",
        "Manual": "Manuel",
        "Tutorial": "Didacticiel",
        "Dependencies": "Dépendances",
        "About Nexuzy Sheet": "À propos de Nexuzy Sheet",
        "Close": "Fermer",
        "Cancel": "Annuler",
        "OK": "OK",
        "License": "Licence",
        "Support": "Assistance",
        "Settings": "Paramètres",
        "New from template": "Nouveau à partir d'un modèle",
        "Offline AI model": "Modèle d'IA hors ligne",
        "AutoFit columns": "Ajustement automatique des colonnes",
        "AutoFit rows": "Ajustement automatique des lignes",
        "AutoFit selection": "Ajustement automatique de la sélection",
    },
    "zh": {
        "File": "文件",
        "Edit": "编辑",
        "View": "视图",
        "Format": "格式",
        "Macro": "宏",
        "Help": "帮助",
        "Language": "语言",
        "Toolbars": "工具栏",
        "New": "新建",
        "Open": "打开",
        "Save": "保存",
        "Save As": "另存为",
        "Import": "导入",
        "Export": "导出",
        "Print": "打印",
        "Print preview": "打印预览",
        "Preferences": "首选项",
        "Quit": "退出",
        "Recent files": "最近使用的文件",
        "Auto save": "自动保存",
        "Version history": "版本历史",
        "Undo": "撤销",
        "Redo": "重做",
        "Cut": "剪切",
        "Copy": "复制",
        "Copy results": "复制结果",
        "Paste": "粘贴",
        "Paste as": "选择性粘贴",
        "Find": "查找",
        "Find next": "查找下一个",
        "Replace": "替换",
        "Sort ascending": "升序排序",
        "Sort descending": "降序排序",
        "Fill down": "向下填充",
        "Fill right": "向右填充",
        "Insert rows": "插入行",
        "Insert columns": "插入列",
        "Delete rows": "删除行",
        "Delete columns": "删除列",
        "Resize grid": "调整网格大小",
        "Fullscreen": "全屏",
        "Dark mode": "深色模式",
        "Zoom in": "放大",
        "Zoom out": "缩小",
        "Go to cell": "转到单元格",
        "Bold": "加粗",
        "Italics": "斜体",
        "Underline": "下划线",
        "Strikethrough": "删除线",
        "Merge cells": "合并单元格",
        "Freeze cell": "冻结单元格",
        "Lock cell": "锁定单元格",
        "Insert image": "插入图片",
        "Insert chart": "插入图表",
        "Insert function": "插入函数",
        "Manual": "手册",
        "Tutorial": "教程",
        "Dependencies": "依赖项",
        "About Nexuzy Sheet": "关于 Nexuzy Sheet",
        "Close": "关闭",
        "Cancel": "取消",
        "OK": "确定",
        "License": "许可证",
        "Support": "支持",
        "Settings": "设置",
        "New from template": "从模板新建",
        "Offline AI model": "离线 AI 模型",
        "AutoFit columns": "自动调整列宽",
        "AutoFit rows": "自动调整行高",
        "AutoFit selection": "自动调整所选内容",
    },
    "ru": {
        "File": "Файл",
        "Edit": "Правка",
        "View": "Вид",
        "Format": "Формат",
        "Macro": "Макрос",
        "Help": "Справка",
        "Language": "Язык",
        "Toolbars": "Панели инструментов",
        "New": "Создать",
        "Open": "Открыть",
        "Save": "Сохранить",
        "Save As": "Сохранить как",
        "Import": "Импорт",
        "Export": "Экспорт",
        "Print": "Печать",
        "Print preview": "Предварительный просмотр",
        "Preferences": "Параметры",
        "Quit": "Выход",
        "Recent files": "Недавние файлы",
        "Auto save": "Автосохранение",
        "Version history": "История версий",
        "Undo": "Отменить",
        "Redo": "Повторить",
        "Cut": "Вырезать",
        "Copy": "Копировать",
        "Copy results": "Копировать результаты",
        "Paste": "Вставить",
        "Paste as": "Специальная вставка",
        "Find": "Найти",
        "Find next": "Найти далее",
        "Replace": "Заменить",
        "Sort ascending": "Сортировка по возрастанию",
        "Sort descending": "Сортировка по убыванию",
        "Fill down": "Заполнить вниз",
        "Fill right": "Заполнить вправо",
        "Insert rows": "Вставить строки",
        "Insert columns": "Вставить столбцы",
        "Delete rows": "Удалить строки",
        "Delete columns": "Удалить столбцы",
        "Resize grid": "Изменить размер сетки",
        "Fullscreen": "Полноэкранный режим",
        "Dark mode": "Тёмная тема",
        "Zoom in": "Увеличить",
        "Zoom out": "Уменьшить",
        "Go to cell": "Перейти к ячейке",
        "Bold": "Полужирный",
        "Italics": "Курсив",
        "Underline": "Подчёркнутый",
        "Strikethrough": "Зачёркнутый",
        "Merge cells": "Объединить ячейки",
        "Freeze cell": "Закрепить ячейку",
        "Lock cell": "Заблокировать ячейку",
        "Insert image": "Вставить изображение",
        "Insert chart": "Вставить диаграмму",
        "Insert function": "Вставить функцию",
        "Manual": "Руководство",
        "Tutorial": "Учебник",
        "Dependencies": "Зависимости",
        "About Nexuzy Sheet": "О программе Nexuzy Sheet",
        "Close": "Закрыть",
        "Cancel": "Отмена",
        "OK": "ОК",
        "License": "Лицензия",
        "Support": "Поддержка",
        "Settings": "Настройки",
        "New from template": "Создать из шаблона",
        "Offline AI model": "Автономная модель ИИ",
        "AutoFit columns": "Автоподбор ширины столбцов",
        "AutoFit rows": "Автоподбор высоты строк",
        "AutoFit selection": "Автоподбор выделения",
    },
    "ja": {
        "File": "ファイル",
        "Edit": "編集",
        "View": "表示",
        "Format": "書式",
        "Macro": "マクロ",
        "Help": "ヘルプ",
        "Language": "言語",
        "Toolbars": "ツールバー",
        "New": "新規",
        "Open": "開く",
        "Save": "保存",
        "Save As": "名前を付けて保存",
        "Import": "インポート",
        "Export": "エクスポート",
        "Print": "印刷",
        "Print preview": "印刷プレビュー",
        "Preferences": "環境設定",
        "Quit": "終了",
        "Recent files": "最近使ったファイル",
        "Auto save": "自動保存",
        "Version history": "バージョン履歴",
        "Undo": "元に戻す",
        "Redo": "やり直す",
        "Cut": "切り取り",
        "Copy": "コピー",
        "Copy results": "結果をコピー",
        "Paste": "貼り付け",
        "Paste as": "形式を選択して貼り付け",
        "Find": "検索",
        "Find next": "次を検索",
        "Replace": "置換",
        "Sort ascending": "昇順で並べ替え",
        "Sort descending": "降順で並べ替え",
        "Fill down": "下方向にコピー",
        "Fill right": "右方向にコピー",
        "Insert rows": "行の挿入",
        "Insert columns": "列の挿入",
        "Delete rows": "行の削除",
        "Delete columns": "列の削除",
        "Resize grid": "グリッドのサイズ変更",
        "Fullscreen": "全画面表示",
        "Dark mode": "ダークモード",
        "Zoom in": "拡大",
        "Zoom out": "縮小",
        "Go to cell": "セルへ移動",
        "Bold": "太字",
        "Italics": "斜体",
        "Underline": "下線",
        "Strikethrough": "取り消し線",
        "Merge cells": "セルの結合",
        "Freeze cell": "セルの固定",
        "Lock cell": "セルのロック",
        "Insert image": "画像を挿入",
        "Insert chart": "グラフを挿入",
        "Insert function": "関数を挿入",
        "Manual": "マニュアル",
        "Tutorial": "チュートリアル",
        "Dependencies": "依存関係",
        "About Nexuzy Sheet": "Nexuzy Sheet について",
        "Close": "閉じる",
        "Cancel": "キャンセル",
        "OK": "OK",
        "License": "ライセンス",
        "Support": "サポート",
        "Settings": "設定",
        "New from template": "テンプレートから新規作成",
        "Offline AI model": "オフライン AI モデル",
        "AutoFit columns": "列幅を自動調整",
        "AutoFit rows": "行の高さを自動調整",
        "AutoFit selection": "選択範囲を自動調整",
    },
}

#: Literal name of the action property that stores the untranslated text
_ORIGINAL_PROPERTY = "_nxsheet_source_text"

_current_language = DEFAULT_LANGUAGE


def set_language(code: str) -> str:
    """Selects the user interface language

    :param code: Language code such as ``"hi"`` or ``"ja"``
    :return: The language code that is active afterwards

    """

    global _current_language

    if code not in LANGUAGES:
        code = DEFAULT_LANGUAGE
    _current_language = code
    return _current_language


def current_language() -> str:
    """Returns the active language code"""

    return _current_language


def language_name(code: str = None) -> str:
    """Returns the native name of a language

    :param code: Language code, defaults to the active language

    """

    return LANGUAGES.get(code or _current_language,
                         LANGUAGES[DEFAULT_LANGUAGE])


def tr(text: str) -> str:
    """Translates an English source string into the active language

    :param text: English source string such as ``"&File"``
    :return: Translated string, or the unchanged text if no entry exists

    """

    if not text:
        return text

    catalog = TRANSLATIONS.get(_current_language, {})
    if not catalog:
        return text

    key = text.replace("&", "")
    if key in catalog:
        return catalog[key]

    stripped = key.rstrip(". ")
    if stripped in catalog:
        return catalog[stripped]

    return text


def apply_to(root) -> int:
    """Translates all actions below a widget tree

    The English source text is remembered in an action property so that the
    language can be changed multiple times without losing the original.

    :param root: Widget such as the main window or a menu bar
    :return: Number of translated actions

    """

    if root is None:
        return 0

    translated = 0
    for action in root.findChildren(QAction):
        text = action.text()
        if not text:
            continue

        source = action.property(_ORIGINAL_PROPERTY)
        if source is None:
            source = text
            action.setProperty(_ORIGINAL_PROPERTY, source)

        target = tr(source)
        if target != action.text():
            action.setText(target)
        if target != source:
            translated += 1

    return translated
