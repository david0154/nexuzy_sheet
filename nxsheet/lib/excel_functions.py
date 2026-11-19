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

Excel compatible spreadsheet functions that are available inside every
Nexuzy Sheet cell, e.g. ``=SUM(S[0:10, 0, 0])`` or ``SUM(S[0:10, 0, 0])``.

* :data:`EXCEL_FUNCTIONS`: Maps function name to callable
* :data:`EXCEL_FUNCTION_NAMES`: Sorted tuple of all function names
* :data:`EXCEL_FUNCTION_DOCS`: Maps function name to (signature, description)

All functions accept plain scalars as well as numpy arrays, lists, tuples,
generators and selections of cells. ``None`` values, empty strings and
booleans are ignored by numeric aggregations, which follows Excel behaviour
for cell ranges.

"""

import fnmatch
import math
import numbers
import random as _random
from datetime import date as _date
from datetime import datetime as _datetime
from datetime import timedelta as _timedelta


MISSING = "#N/A"
VALUE_ERROR = "#VALUE!"
DIV_ZERO = "#DIV/0!"


def _iter_scalars(value):
    """Yields scalar values from nested iterables and cell ranges

    :param value: Arbitrary value that may contain nested iterables

    """

    if value is None:
        return

    if isinstance(value, (str, bytes, dict)):
        yield value
        return

    try:
        iterator = iter(value)
    except TypeError:
        yield value
        return

    for item in iterator:
        if item is None:
            continue
        if isinstance(item, (str, bytes, dict)):
            yield item
            continue
        try:
            iter(item)
        except TypeError:
            yield item
        else:
            for sub_item in _iter_scalars(item):
                yield sub_item


def _numbers(*values):
    """Returns list of numbers from arbitrary nested values"""

    collected = []
    for value in _iter_scalars(values):
        if isinstance(value, bool):
            continue
        if isinstance(value, numbers.Real):
            if isinstance(value, float) and math.isnan(value):
                continue
            collected.append(float(value))
    return collected


def _texts(*values):
    """Returns list of non empty strings from arbitrary nested values"""

    texts = []
    for value in _iter_scalars(values):
        if value is None:
            continue
        text = str(value)
        if text:
            texts.append(text)
    return texts


def _as_number(value):
    """Tries to convert value into float, returns None on failure"""

    if isinstance(value, bool):
        return None
    if isinstance(value, numbers.Real):
        return float(value)
    if isinstance(value, str):
        return _parse_number(value)
    return None


def _parse_number(text):
    """Parses a number from text, returns None on failure"""

    cleaned = text.strip().replace(",", "").replace(" ", "")
    if not cleaned:
        return None
    for symbol in ("₹", "$", "€", "£", "¥"):
        cleaned = cleaned.replace(symbol, "")
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1]
    percent = cleaned.endswith("%")
    if percent:
        cleaned = cleaned[:-1]
    try:
        result = float(cleaned)
    except ValueError:
        return None
    if percent:
        result /= 100.0
    return -result if negative else result


def _match_value(value, criteria):
    """Excel like criteria matching including comparison operators

    :param value: Cell value to be checked
    :param criteria: Criteria such as ``">5"``, ``"<>done"`` or ``"apple*"``

    """

    if criteria is None:
        return value is None

    if isinstance(criteria, str):
        text = criteria.strip()
        for operator in (">=", "<=", "<>", ">", "<", "="):
            if text.startswith(operator):
                operand = text[len(operator):].strip()
                number_operand = _parse_number(operand)
                number_value = _as_number(value)
                not_equal = operator == "<>"

                if number_operand is not None and number_value is not None:
                    comparisons = {">=": number_value >= number_operand,
                                   "<=": number_value <= number_operand,
                                   ">": number_value > number_operand,
                                   "<": number_value < number_operand,
                                   "=": number_value == number_operand,
                                   "<>": number_value != number_operand}
                    return comparisons[operator]

                value_text = "" if value is None else str(value).casefold()
                operand_text = operand.casefold()
                if not_equal:
                    return value_text != operand_text
                if any(char in operand_text for char in "*?["):
                    return fnmatch.fnmatchcase(value_text, operand_text)
                return value_text == operand_text

        value_number = _as_number(value)
        criteria_number = _parse_number(text)
        if value_number is not None and criteria_number is not None:
            return math.isclose(value_number, criteria_number, rel_tol=1e-9,
                                abs_tol=1e-9)

        value_text = "" if value is None else str(value).casefold()
        if any(char in text.casefold() for char in "*?["):
            return fnmatch.fnmatchcase(value_text, text.casefold())
        return value_text == text.casefold()

    number_criteria = _as_number(criteria)
    number_value = _as_number(value)
    if number_criteria is not None and number_value is not None:
        return math.isclose(number_value, number_criteria, rel_tol=1e-9,
                            abs_tol=1e-9)
    return value == criteria


def _criteria_pairs(criteria, *ranges):
    """Yields tuples of aligned values for the given ranges"""

    aligned = [[item for item in _iter_scalars(r)] for r in ranges]
    length = max((len(row) for row in aligned), default=0)
    for index in range(length):
        yield tuple(row[index] if index < len(row) else None
                    for row in aligned)


def _is_error(value):
    """True if value is an Excel error marker or an exception"""

    if isinstance(value, BaseException):
        return True
    return isinstance(value, str) and value in (MISSING, VALUE_ERROR, DIV_ZERO)


# Mathematical functions
# ----------------------


def SUM(*values):
    """SUM(number1, [number2], ...) - Sums all numbers"""

    return sum(_numbers(values))


def SUMSQ(*values):
    """SUMSQ(number1, [number2], ...) - Sum of squares"""

    return sum(number ** 2 for number in _numbers(values))


def PRODUCT(*values):
    """PRODUCT(number1, [number2], ...) - Multiplies all numbers"""

    numbers = _numbers(values)
    return math.prod(numbers) if numbers else 0


def AVERAGE(*values):
    """AVERAGE(number1, [number2], ...) - Arithmetic mean"""

    numbers = _numbers(values)
    if not numbers:
        return DIV_ZERO
    return sum(numbers) / len(numbers)


def COUNT(*values):
    """COUNT(value1, [value2], ...) - Number of numeric values"""

    return len(_numbers(values))


def COUNTA(*values):
    """COUNTA(value1, [value2], ...) - Number of non empty values"""

    return len(_texts(values))


def COUNTBLANK(*values):
    """COUNTBLANK(range1, [range2], ...) - Number of empty values"""

    return sum(1 for value in _iter_scalars(values)
               if value is None or value == "")


def MAX(*values):
    """MAX(number1, [number2], ...) - Largest number"""

    numbers = _numbers(values)
    return max(numbers) if numbers else 0


def MIN(*values):
    """MIN(number1, [number2], ...) - Smallest number"""

    numbers = _numbers(values)
    return min(numbers) if numbers else 0


def MEDIAN(*values):
    """MEDIAN(number1, [number2], ...) - Median"""

    numbers = sorted(_numbers(values))
    if not numbers:
        return DIV_ZERO
    middle = len(numbers) // 2
    if len(numbers) % 2:
        return numbers[middle]
    return (numbers[middle - 1] + numbers[middle]) / 2


def STDEV(*values):
    """STDEV(number1, [number2], ...) - Sample standard deviation"""

    numbers = _numbers(values)
    if len(numbers) < 2:
        return DIV_ZERO
    mean = sum(numbers) / len(numbers)
    variance = sum((n - mean) ** 2 for n in numbers) / (len(numbers) - 1)
    return math.sqrt(variance)


def STDEVP(*values):
    """STDEVP(number1, [number2], ...) - Population standard deviation"""

    numbers = _numbers(values)
    if not numbers:
        return DIV_ZERO
    mean = sum(numbers) / len(numbers)
    return math.sqrt(sum((n - mean) ** 2 for n in numbers) / len(numbers))


def VAR(*values):
    """VAR(number1, [number2], ...) - Sample variance"""

    numbers = _numbers(values)
    if len(numbers) < 2:
        return DIV_ZERO
    mean = sum(numbers) / len(numbers)
    return sum((n - mean) ** 2 for n in numbers) / (len(numbers) - 1)


def VARP(*values):
    """VARP(number1, [number2], ...) - Population variance"""

    numbers = _numbers(values)
    if not numbers:
        return DIV_ZERO
    mean = sum(numbers) / len(numbers)
    return sum((n - mean) ** 2 for n in numbers) / len(numbers)


def SUMPRODUCT(range1, range2):
    """SUMPRODUCT(range1, range2) - Sum of element wise products"""

    total = 0.0
    for left, right in _criteria_pairs(None, range1, range2):
        left_number = _as_number(left)
        right_number = _as_number(right)
        if left_number is None or right_number is None:
            continue
        total += left_number * right_number
    return total


def SUMIF(range, criteria, sum_range=None):
    """SUMIF(range, criteria, [sum_range]) - Sums values matching criteria"""

    if sum_range is None:
        return sum(_as_number(value) or 0.0
                   for value in _iter_scalars(range)
                   if _match_value(value, criteria))
    total = 0.0
    for value, target in _criteria_pairs(criteria, range, sum_range):
        if _match_value(value, criteria):
            number = _as_number(target)
            if number is not None:
                total += number
    return total


def COUNTIF(range, criteria):
    """COUNTIF(range, criteria) - Counts values matching criteria"""

    return sum(1 for value in _iter_scalars(range)
               if _match_value(value, criteria))


def AVERAGEIF(range, criteria, average_range=None):
    """AVERAGEIF(range, criteria, [average_range]) - Mean of matching values"""

    if average_range is None:
        numbers = [_as_number(value) for value in _iter_scalars(range)
                   if _match_value(value, criteria)]
    else:
        numbers = [_as_number(target)
                   for value, target in _criteria_pairs(criteria, range,
                                                        average_range)
                   if _match_value(value, criteria)]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return DIV_ZERO
    return sum(numbers) / len(numbers)


def LARGE(range, k):
    """LARGE(range, k) - k-th largest value"""

    numbers = sorted(_numbers(range), reverse=True)
    k = int(k)
    if not 1 <= k <= len(numbers):
        return VALUE_ERROR
    return numbers[k - 1]


def SMALL(range, k):
    """SMALL(range, k) - k-th smallest value"""

    numbers = sorted(_numbers(range))
    k = int(k)
    if not 1 <= k <= len(numbers):
        return VALUE_ERROR
    return numbers[k - 1]


def RANK(number, range, order=0):
    """RANK(number, range, [order]) - Rank of number inside range"""

    numbers = sorted(_numbers(range), reverse=bool(order))
    number = _as_number(number)
    if number is None:
        return VALUE_ERROR
    for position, candidate in enumerate(numbers, start=1):
        if math.isclose(candidate, number, rel_tol=1e-9, abs_tol=1e-9):
            return position
    return MISSING


def ABS(number):
    """ABS(number) - Absolute value"""

    return abs(_as_number(number) or 0.0)


def SIGN(number):
    """SIGN(number) - Sign of a number"""

    number = _as_number(number) or 0.0
    return (number > 0) - (number < 0)


def POWER(number, power):
    """POWER(number, power) - Number raised to a power"""

    return (_as_number(number) or 0.0) ** (_as_number(power) or 0.0)


def SQRT(number):
    """SQRT(number) - Square root"""

    number = _as_number(number) or 0.0
    if number < 0:
        return VALUE_ERROR
    return math.sqrt(number)


def EXP(number):
    """EXP(number) - e raised to a number"""

    return math.exp(_as_number(number) or 0.0)


def LN(number):
    """LN(number) - Natural logarithm"""

    number = _as_number(number) or 0.0
    if number <= 0:
        return VALUE_ERROR
    return math.log(number)


def LOG(number, base=10):
    """LOG(number, [base]) - Logarithm to a given base"""

    number = _as_number(number) or 0.0
    base = _as_number(base) or 10.0
    if number <= 0 or base <= 0 or base == 1:
        return VALUE_ERROR
    return math.log(number, base)


def LOG10(number):
    """LOG10(number) - Logarithm to base 10"""

    return LOG(number, 10)


def PI():
    """PI() - The constant pi"""

    return math.pi


def RAND():
    """RAND() - Random number between 0 and 1"""

    return _random.random()


def RANDBETWEEN(bottom, top):
    """RANDBETWEEN(bottom, top) - Random integer between both values"""

    bottom = int(_as_number(bottom) or 0)
    top = int(_as_number(top) or 0)
    if top < bottom:
        bottom, top = top, bottom
    return _random.randint(bottom, top)


def _round_half_away(number, digits=0):
    """Rounds half away from zero like Excel does"""

    factor = 10.0 ** int(digits)
    value = float(number) * factor
    if value >= 0:
        rounded = math.floor(value + 0.5)
    else:
        rounded = math.ceil(value - 0.5)
    return rounded / factor


def ROUND(number, digits=0):
    """ROUND(number, [digits]) - Rounds half away from zero"""

    return _round_half_away(_as_number(number) or 0.0, digits)


def ROUNDUP(number, digits=0):
    """ROUNDUP(number, [digits]) - Rounds away from zero"""

    factor = 10.0 ** int(digits)
    value = (_as_number(number) or 0.0) * factor
    return (math.ceil(value) if value >= 0 else math.floor(value)) / factor


def ROUNDDOWN(number, digits=0):
    """ROUNDDOWN(number, [digits]) - Rounds towards zero"""

    factor = 10.0 ** int(digits)
    value = (_as_number(number) or 0.0) * factor
    return (math.floor(value) if value >= 0 else math.ceil(value)) / factor


def INT(number):
    """INT(number) - Rounds down to the nearest integer"""

    return math.floor(_as_number(number) or 0.0)


def TRUNC(number, digits=0):
    """TRUNC(number, [digits]) - Truncates to an integer"""

    return ROUNDDOWN(number, digits)


def MOD(number, divisor):
    """MOD(number, divisor) - Remainder with the sign of the divisor"""

    divisor = _as_number(divisor) or 0.0
    if divisor == 0:
        return DIV_ZERO
    number = _as_number(number) or 0.0
    return number - divisor * math.floor(number / divisor)


def MROUND(number, multiple):
    """MROUND(number, multiple) - Rounds to the nearest multiple"""

    multiple = _as_number(multiple) or 0.0
    if multiple == 0:
        return 0
    number = _as_number(number) or 0.0
    return _round_half_away(number / multiple) * multiple


def CEILING(number, significance=1):
    """CEILING(number, [significance]) - Rounds up to a multiple"""

    significance = _as_number(significance) or 1.0
    if significance == 0:
        return 0
    number = _as_number(number) or 0.0
    return math.ceil(number / significance) * significance


def FLOOR(number, significance=1):
    """FLOOR(number, [significance]) - Rounds down to a multiple"""

    significance = _as_number(significance) or 1.0
    if significance == 0:
        return 0
    number = _as_number(number) or 0.0
    return math.floor(number / significance) * significance


def GCD(*values):
    """GCD(number1, [number2], ...) - Greatest common divisor"""

    numbers = [int(number) for number in _numbers(values)]
    if not numbers:
        return 0
    result = numbers[0]
    for number in numbers[1:]:
        result = math.gcd(result, number)
    return abs(result)


def LCM(*values):
    """LCM(number1, [number2], ...) - Least common multiple"""

    numbers = [int(number) for number in _numbers(values)]
    if not numbers:
        return 0
    result = numbers[0]
    for number in numbers[1:]:
        if result == 0 or number == 0:
            return 0
        result = abs(result * number) // math.gcd(result, number)
    return result


# Logical functions
# -----------------


def IF(condition, value_if_true, value_if_false=False):
    """IF(condition, value_if_true, [value_if_false]) - Conditional value"""

    return value_if_true if condition else value_if_false


def IFERROR(value, value_if_error):
    """IFERROR(value, value_if_error) - Fallback for errors"""

    return value_if_error if _is_error(value) else value


def IFNA(value, value_if_na):
    """IFNA(value, value_if_na) - Fallback for #N/A only"""

    if value == MISSING:
        return value_if_na
    return value


def AND(*values):
    """AND(logical1, [logical2], ...) - True if all values are true"""

    return all(bool(value) for value in _iter_scalars(values)
               if value is not None)


def OR(*values):
    """OR(logical1, [logical2], ...) - True if any value is true"""

    return any(bool(value) for value in _iter_scalars(values)
               if value is not None)


def NOT(value):
    """NOT(logical) - Inverts a logical value"""

    return not value


def XOR(*values):
    """XOR(logical1, [logical2], ...) - True for an odd number of trues"""

    return sum(1 for value in _iter_scalars(values) if value) % 2 == 1


def TRUE():
    """TRUE() - The logical value true"""

    return True


def FALSE():
    """FALSE() - The logical value false"""

    return False


def ISBLANK(value):
    """ISBLANK(value) - True for empty cells"""

    return value is None or value == ""


def ISNUMBER(value):
    """ISNUMBER(value) - True for numbers"""

    return _as_number(value) is not None


def ISTEXT(value):
    """ISTEXT(value) - True for text"""

    return isinstance(value, str) and _parse_number(value) is None


def ISERROR(value):
    """ISERROR(value) - True for errors"""

    return _is_error(value)


def ISNA(value):
    """ISNA(value) - True for #N/A"""

    return value == MISSING


def NA():
    """NA() - The #N/A error value"""

    return MISSING


# Text functions
# --------------


def CONCATENATE(*values):
    """CONCATENATE(text1, [text2], ...) - Joins values into one text"""

    return "".join("" if value is None else str(value)
                   for value in _iter_scalars(values))


def CONCAT(*values):
    """CONCAT(text1, [text2], ...) - Joins values into one text"""

    return CONCATENATE(*values)


def TEXTJOIN(delimiter, ignore_empty, *values):
    """TEXTJOIN(delimiter, ignore_empty, text1, ...) - Joins with delimiter"""

    delimiter = "" if delimiter is None else str(delimiter)
    items = ["" if value is None else str(value)
             for value in _iter_scalars(values)]
    if ignore_empty:
        items = [item for item in items if item]
    return delimiter.join(items)


def LEFT(text, num_chars=1):
    """LEFT(text, [num_chars]) - First characters of a text"""

    return str("" if text is None else text)[:int(num_chars)]


def RIGHT(text, num_chars=1):
    """RIGHT(text, [num_chars]) - Last characters of a text"""

    num_chars = int(num_chars)
    text = str("" if text is None else text)
    return text[-num_chars:] if num_chars else ""


def MID(text, start_num, num_chars):
    """MID(text, start_num, num_chars) - Substring starting at 1"""

    start = max(int(start_num) - 1, 0)
    return str("" if text is None else text)[start:start + int(num_chars)]


def LEN(text):
    """LEN(text) - Number of characters"""

    return len(str("" if text is None else text))


def UPPER(text):
    """UPPER(text) - Converts text to upper case"""

    return str("" if text is None else text).upper()


def LOWER(text):
    """LOWER(text) - Converts text to lower case"""

    return str("" if text is None else text).lower()


def PROPER(text):
    """PROPER(text) - Capitalizes each word"""

    return str("" if text is None else text).title()


def TRIM(text):
    """TRIM(text) - Removes leading, trailing and double spaces"""

    return " ".join(str("" if text is None else text).split())


def SUBSTITUTE(text, old_text, new_text, instance_num=None):
    """SUBSTITUTE(text, old, new, [instance_num]) - Replaces text"""

    text = str("" if text is None else text)
    old_text = str(old_text)
    new_text = "" if new_text is None else str(new_text)
    if instance_num is None:
        return text.replace(old_text, new_text)

    instance_num = int(instance_num)
    if instance_num < 1:
        return text

    replaced = 0
    result = []
    index = 0
    while index < len(text):
        if text.startswith(old_text, index) and old_text:
            replaced += 1
            if replaced == instance_num:
                result.append(new_text)
            else:
                result.append(old_text)
            index += len(old_text)
        else:
            result.append(text[index])
            index += 1
    return "".join(result)


def REPLACE(old_text, start_num, num_chars, new_text):
    """REPLACE(old_text, start_num, num_chars, new_text) - Replaces by pos"""

    old_text = str("" if old_text is None else old_text)
    start = max(int(start_num) - 1, 0)
    end = start + int(num_chars)
    return old_text[:start] + str("" if new_text is None else new_text) \
        + old_text[end:]


def FIND(find_text, within_text, start_num=1):
    """FIND(find_text, within_text, [start_num]) - Case sensitive search"""

    find_text = str(find_text)
    within_text = str("" if within_text is None else within_text)
    position = within_text.find(find_text, max(int(start_num) - 1, 0))
    if position < 0:
        return VALUE_ERROR
    return position + 1


def SEARCH(find_text, within_text, start_num=1):
    """SEARCH(find_text, within_text, [start_num]) - Case insensitive search"""

    find_text = str(find_text).casefold()
    within_text = str("" if within_text is None else within_text).casefold()
    position = within_text.find(find_text, max(int(start_num) - 1, 0))
    if position < 0:
        return VALUE_ERROR
    return position + 1


def EXACT(text1, text2):
    """EXACT(text1, text2) - Case sensitive text comparison"""

    return str(text1) == str(text2)


def REPT(text, number_times):
    """REPT(text, number_times) - Repeats text"""

    return str("" if text is None else text) * max(int(number_times), 0)


def NUMBERVALUE(text):
    """NUMBERVALUE(text) - Converts text into a number"""

    number = _parse_number(str("" if text is None else text))
    return VALUE_ERROR if number is None else number


VALUE = NUMBERVALUE
"""VALUE(text) - Converts text into a number"""


def DOLLAR(number, decimals=2):
    """DOLLAR(number, [decimals]) - Formats a number as currency"""

    number = _as_number(number) or 0.0
    return f"${number:,.{int(decimals)}f}"


def FIXED(number, decimals=2, no_commas=False):
    """FIXED(number, [decimals], [no_commas]) - Formats a number as text"""

    number = _as_number(number) or 0.0
    decimals = int(decimals)
    if no_commas:
        return f"{number:.{decimals}f}"
    return f"{number:,.{decimals}f}"


def TEXT(value, format_text="General"):
    """TEXT(value, format_text) - Formats a value as Excel style text"""

    if value is None:
        return ""
    if isinstance(format_text, str) \
            and format_text.strip().lower() in ("general", ""):
        return str(value)

    if isinstance(value, (_date, _datetime)) or (
            isinstance(format_text, str)
            and any(token in format_text.lower()
                    for token in ("yyyy", "yy", "dd", "hh", "ss"))):
        return _format_date(value, str(format_text))

    number = _as_number(value)
    if number is None:
        return str(value)
    return _format_number(number, str(format_text))


def _format_date(value, format_text):
    """Formats a date using an Excel like format code"""

    if not isinstance(value, (_date, _datetime)):
        parsed = _parse_date(value)
        if parsed is None:
            return str(value)
        value = parsed

    tokens = (("yyyy", "%Y"), ("yy", "%y"), ("mmmm", "%B"), ("mmm", "%b"),
              ("mm", "%m"), ("dd", "%d"), ("hh", "%H"), ("ss", "%S"),
              ("h", "%H"))
    result = format_text
    for token, replacement in tokens:
        result = result.replace(token, replacement)
    result = result.replace("d", "%d").replace("m", "%m")
    try:
        return value.strftime(result)
    except (ValueError, TypeError):
        return str(value)


def _format_number(number, format_text):
    """Formats a number using an Excel like format code"""

    text = format_text.strip()
    if not text:
        return str(number)

    percent = "%" in text
    text = text.replace("%", "")
    number = number * 100 if percent else number

    if "." in text:
        whole_part, fractional_part = text.split(".", 1)
        decimals = sum(1 for char in fractional_part if char in "0#")
        suffix = "".join(char for char in fractional_part
                         if char not in "0#")
    else:
        whole_part, decimals, suffix = text, 0, ""

    thousands = "," in whole_part
    prefix = "".join(char for char in whole_part if char not in "0#,")
    pattern = f"{number:,.{decimals}f}" if thousands \
        else f"{number:.{decimals}f}"

    result = f"{prefix}{pattern}{suffix}"
    if percent:
        result = f"{result}%"
    return result


def _parse_date(value):
    """Parses a date from text, returns None on failure"""

    if isinstance(value, _datetime):
        return value
    if isinstance(value, _date):
        return value
    text = str(value).strip()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y",
                    "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return _datetime.strptime(text, pattern)
        except ValueError:
            continue
    return None


# Lookup functions
# ----------------


def _table_rows(table):
    """Returns list of rows from a two dimensional table like value"""

    if table is None:
        return []
    if hasattr(table, "tolist"):
        try:
            table = table.tolist()
        except Exception:
            pass
    rows = []
    try:
        iterator = iter(table)
    except TypeError:
        return [[table]]
    for row in iterator:
        if isinstance(row, (str, bytes)):
            rows.append([row])
            continue
        try:
            rows.append(list(row))
        except TypeError:
            rows.append([row])
    return rows


def VLOOKUP(lookup_value, table_array, col_index_num, range_lookup=True):
    """VLOOKUP(value, table, col_index, [range_lookup]) - Vertical lookup"""

    rows = _table_rows(table_array)
    column = int(col_index_num) - 1
    if column < 0:
        return VALUE_ERROR

    def cell(row, index):
        """Returns cell value or None from row"""
        return row[index] if 0 <= index < len(row) else None

    if range_lookup:
        best = None
        for row in rows:
            key = cell(row, 0)
            if _match_value(key, f"<={lookup_value}"):
                best = row
            elif best is None and isinstance(key, str):
                if str(key).casefold() <= str(lookup_value).casefold():
                    best = row
        if best is None:
            return MISSING
        return cell(best, column)

    for row in rows:
        if _match_value(cell(row, 0), lookup_value):
            return cell(row, column)
    return MISSING


def HLOOKUP(lookup_value, table_array, row_index_num, range_lookup=True):
    """HLOOKUP(value, table, row_index, [range_lookup]) - Horizontal lookup"""

    rows = _table_rows(table_array)
    if not rows:
        return MISSING
    header = rows[0]
    row_index = int(row_index_num) - 1
    for column_index, key in enumerate(header):
        if _match_value(key, lookup_value):
            if 0 <= row_index < len(rows) \
                    and column_index < len(rows[row_index]):
                return rows[row_index][column_index]
            return MISSING
    return MISSING


def MATCH(lookup_value, lookup_array, match_type=1):
    """MATCH(value, range, [match_type]) - Position of a value in a range"""

    values = [value for value in _iter_scalars(lookup_array)]
    match_type = int(match_type)

    if match_type == 0:
        for index, value in enumerate(values, start=1):
            if _match_value(value, lookup_value):
                return index
        return MISSING

    best_index = None
    for index, value in enumerate(values, start=1):
        number = _as_number(value)
        target = _as_number(lookup_value)
        if number is not None and target is not None:
            if match_type > 0 and number <= target:
                best_index = index
            elif match_type < 0 and number >= target:
                best_index = index
        elif isinstance(value, str) and isinstance(lookup_value, str):
            if match_type > 0 and value.casefold() <= lookup_value.casefold():
                best_index = index
            elif match_type < 0 \
                    and value.casefold() >= lookup_value.casefold():
                best_index = index
    return best_index if best_index is not None else MISSING


def INDEX(array, row_num, column_num=None):
    """INDEX(array, row_num, [column_num]) - Value at a position"""

    rows = _table_rows(array)
    row_num = int(row_num)
    if column_num is None:
        if row_num == 0:
            return array
        if not 1 <= row_num <= len(rows):
            return MISSING
        return rows[row_num - 1]

    column_num = int(column_num)
    if row_num == 0:
        if not 1 <= column_num <= len(rows[0]):
            return MISSING
        return [row[column_num - 1] for row in rows
                if 0 <= column_num - 1 < len(row)]
    if column_num == 0:
        if not 1 <= row_num <= len(rows):
            return MISSING
        return rows[row_num - 1]

    if not 1 <= row_num <= len(rows):
        return MISSING
    row = rows[row_num - 1]
    if not 1 <= column_num <= len(row):
        return MISSING
    return row[column_num - 1]


def CHOOSE(index_num, *values):
    """CHOOSE(index_num, value1, [value2], ...) - Picks a value"""

    items = list(_iter_scalars(values))
    index = int(index_num)
    if not 1 <= index <= len(items):
        return VALUE_ERROR
    return items[index - 1]


# Date and time functions
# -----------------------


def TODAY():
    """TODAY() - Current date"""

    return _date.today()


def NOW():
    """NOW() - Current date and time"""

    return _datetime.now()


def DATE(year, month, day):
    """DATE(year, month, day) - Builds a date"""

    year = int(year)
    month = int(month)
    day = int(day)
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    return _date(year, month, 1) + _timedelta(days=day - 1)


def TIME(hour, minute, second):
    """TIME(hour, minute, second) - Builds a time"""

    return (_datetime(2000, 1, 1)
            + _timedelta(hours=int(hour), minutes=int(minute),
                         seconds=int(second))).time()


def YEAR(value):
    """YEAR(date) - Year of a date"""

    parsed = _parse_date(value)
    return VALUE_ERROR if parsed is None else parsed.year


def MONTH(value):
    """MONTH(date) - Month of a date"""

    parsed = _parse_date(value)
    return VALUE_ERROR if parsed is None else parsed.month


def DAY(value):
    """DAY(date) - Day of a date"""

    parsed = _parse_date(value)
    return VALUE_ERROR if parsed is None else parsed.day


def HOUR(value):
    """HOUR(time) - Hour of a time"""

    parsed = _parse_date(value)
    if parsed is None:
        return VALUE_ERROR
    return parsed.hour


def MINUTE(value):
    """MINUTE(time) - Minute of a time"""

    parsed = _parse_date(value)
    if parsed is None:
        return VALUE_ERROR
    return parsed.minute


def SECOND(value):
    """SECOND(time) - Second of a time"""

    parsed = _parse_date(value)
    if parsed is None:
        return VALUE_ERROR
    return parsed.second


def WEEKDAY(value, return_type=1):
    """WEEKDAY(date, [return_type]) - Day of week"""

    parsed = _parse_date(value)
    if parsed is None:
        return VALUE_ERROR
    weekday = parsed.weekday()  # Monday is 0
    if int(return_type) == 2:
        return weekday + 1
    if int(return_type) == 3:
        return weekday
    return (weekday + 1) % 7 + 1


def DAYS(end_date, start_date):
    """DAYS(end_date, start_date) - Number of days between two dates"""

    end = _parse_date(end_date)
    start = _parse_date(start_date)
    if end is None or start is None:
        return VALUE_ERROR
    return (end - start).days


def EDATE(start_date, months):
    """EDATE(start_date, months) - Date shifted by months"""

    parsed = _parse_date(start_date)
    if parsed is None:
        return VALUE_ERROR
    months = int(months)
    year = parsed.year + (parsed.month - 1 + months) // 12
    month = (parsed.month - 1 + months) % 12 + 1
    day = min(parsed.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                           31, 31, 30, 31, 30, 31][month - 1])
    return _date(year, month, day)


def EOMONTH(start_date, months=0):
    """EOMONTH(start_date, [months]) - Last day of the shifted month"""

    shifted = EDATE(start_date, months)
    if shifted == VALUE_ERROR:
        return VALUE_ERROR
    shifted = EDATE(shifted.replace(day=1), 1)
    return shifted - _timedelta(days=1)


def NETWORKDAYS(start_date, end_date, holidays=None):
    """NETWORKDAYS(start, end, [holidays]) - Working days between dates"""

    start = _parse_date(start_date)
    end = _parse_date(end_date)
    if start is None or end is None:
        return VALUE_ERROR
    holiday_dates = set()
    for holiday in _iter_scalars(holidays):
        parsed = _parse_date(holiday)
        if parsed is not None:
            holiday_dates.add(parsed.date())
    if start > end:
        start, end = end, start
    days = 0
    current = start.date()
    end = end.date()
    while current <= end:
        if current.weekday() < 5 and current not in holiday_dates:
            days += 1
        current += _timedelta(days=1)
    return days


# Financial functions
# -------------------


def FV(rate, nper, pmt, pv=0, when=0):
    """FV(rate, nper, pmt, [pv], [when]) - Future value"""

    rate = _as_number(rate) or 0.0
    nper = _as_number(nper) or 0.0
    pmt = _as_number(pmt) or 0.0
    pv = _as_number(pv) or 0.0
    when = int(when)

    if rate == 0:
        return -(pv + pmt * nper)
    factor = (1 + rate) ** nper
    return -(pv * factor + pmt * (1 + rate * when) * (factor - 1) / rate)


def PV(rate, nper, pmt, fv=0, when=0):
    """PV(rate, nper, pmt, [fv], [when]) - Present value"""

    rate = _as_number(rate) or 0.0
    nper = _as_number(nper) or 0.0
    pmt = _as_number(pmt) or 0.0
    fv = _as_number(fv) or 0.0
    when = int(when)

    if rate == 0:
        return -(fv + pmt * nper)
    factor = (1 + rate) ** nper
    return -(fv + pmt * (1 + rate * when) * (factor - 1) / rate) / factor


def PMT(rate, nper, pv, fv=0, when=0):
    """PMT(rate, nper, pv, [fv], [when]) - Periodic payment"""

    rate = _as_number(rate) or 0.0
    nper = _as_number(nper) or 0.0
    pv = _as_number(pv) or 0.0
    fv = _as_number(fv) or 0.0
    when = int(when)

    if nper == 0:
        return DIV_ZERO
    if rate == 0:
        return -(pv + fv) / nper
    factor = (1 + rate) ** nper
    return -(rate * (pv * factor + fv)) / \
        ((1 + rate * when) * (factor - 1))


def NPV(rate, *values):
    """NPV(rate, value1, [value2], ...) - Net present value"""

    rate = _as_number(rate) or 0.0
    if rate == -1:
        return DIV_ZERO
    return sum(number / (1 + rate) ** period
               for period, number in enumerate(_numbers(values), start=1))


def IRR(values, guess=0.1):
    """IRR(values, [guess]) - Internal rate of return"""

    cash_flows = _numbers(values)
    if not cash_flows or not any(cf < 0 for cf in cash_flows) \
            or not any(cf > 0 for cf in cash_flows):
        return VALUE_ERROR

    def npv(rate):
        """NPV helper for IRR"""
        return sum(cf / (1 + rate) ** period
                   for period, cf in enumerate(cash_flows))

    low, high = -0.9999, 10.0
    if npv(low) * npv(high) > 0:
        return VALUE_ERROR
    for _ in range(200):
        middle = (low + high) / 2
        value = npv(middle)
        if abs(value) < 1e-9:
            return middle
        if npv(low) * value < 0:
            high = middle
        else:
            low = middle
    return (low + high) / 2


def EFFECT(nominal_rate, npery):
    """EFFECT(nominal_rate, npery) - Effective annual interest rate"""

    nominal_rate = _as_number(nominal_rate) or 0.0
    npery = int(_as_number(npery) or 0)
    if npery < 1:
        return VALUE_ERROR
    return (1 + nominal_rate / npery) ** npery - 1


def NPER(rate, pmt, pv, fv=0, when=0):
    """NPER(rate, pmt, pv, [fv], [when]) - Number of periods"""

    rate = _as_number(rate) or 0.0
    pmt = _as_number(pmt) or 0.0
    pv = _as_number(pv) or 0.0
    fv = _as_number(fv) or 0.0
    when = int(when)

    if rate == 0:
        if pmt == 0:
            return DIV_ZERO
        return -(pv + fv) / pmt
    if pmt * (1 + rate * when) - fv * rate == 0:
        return DIV_ZERO
    try:
        return math.log((pmt * (1 + rate * when) - fv * rate)
                        / (pv * rate + pmt * (1 + rate * when))) \
            / math.log(1 + rate)
    except (ValueError, ZeroDivisionError):
        return VALUE_ERROR


EXCEL_FUNCTIONS = {
    name: value
    for name, value in list(globals().items())
    if name.isupper() and callable(value) and not name.startswith("_")
}

EXCEL_FUNCTION_NAMES = tuple(sorted(EXCEL_FUNCTIONS))


EXCEL_FUNCTION_DOCS = {
    "ABS": ("ABS(number)", "Absolute value of a number."),
    "AND": ("AND(logical1, [logical2], ...)",
            "True if all arguments are true."),
    "AVERAGE": ("AVERAGE(number1, [number2], ...)",
                "Arithmetic mean of the numeric arguments."),
    "AVERAGEIF": ("AVERAGEIF(range, criteria, [average_range])",
                  "Mean of the values that match a criteria."),
    "CEILING": ("CEILING(number, [significance])",
                "Rounds a number up to the nearest multiple."),
    "CHOOSE": ("CHOOSE(index_num, value1, [value2], ...)",
               "Returns the value at a 1-based index."),
    "CONCAT": ("CONCAT(text1, [text2], ...)", "Joins values into one text."),
    "CONCATENATE": ("CONCATENATE(text1, [text2], ...)",
                    "Joins values into one text."),
    "COUNT": ("COUNT(value1, [value2], ...)",
              "Counts the numeric values."),
    "COUNTA": ("COUNTA(value1, [value2], ...)",
               "Counts all non empty values."),
    "COUNTBLANK": ("COUNTBLANK(range1, [range2], ...)",
                   "Counts empty cells."),
    "COUNTIF": ("COUNTIF(range, criteria)",
                "Counts the values that match a criteria."),
    "DATE": ("DATE(year, month, day)", "Builds a date value."),
    "DAYS": ("DAYS(end_date, start_date)",
             "Number of days between two dates."),
    "DOLLAR": ("DOLLAR(number, [decimals])",
               "Formats a number as currency text."),
    "EDATE": ("EDATE(start_date, months)",
              "Date shifted by a number of months."),
    "EFFECT": ("EFFECT(nominal_rate, npery)",
               "Effective annual interest rate."),
    "EOMONTH": ("EOMONTH(start_date, [months])",
                "Last day of the month after shifting."),
    "EXACT": ("EXACT(text1, text2)",
              "Case sensitive text comparison."),
    "EXP": ("EXP(number)", "e raised to a number."),
    "FALSE": ("FALSE()", "The logical value false."),
    "FIND": ("FIND(find_text, within_text, [start_num])",
             "Case sensitive text search, 1-based position."),
    "FIXED": ("FIXED(number, [decimals], [no_commas])",
              "Formats a number as text with fixed decimals."),
    "FLOOR": ("FLOOR(number, [significance])",
              "Rounds a number down to the nearest multiple."),
    "FV": ("FV(rate, nper, pmt, [pv], [when])", "Future value of an annuity."),
    "GCD": ("GCD(number1, [number2], ...)", "Greatest common divisor."),
    "HLOOKUP": ("HLOOKUP(value, table, row_index, [range_lookup])",
                "Searches the first row and returns a row below it."),
    "HOUR": ("HOUR(time)", "Hour of a time value."),
    "IF": ("IF(condition, value_if_true, [value_if_false])",
           "Returns one of two values depending on a condition."),
    "IFERROR": ("IFERROR(value, value_if_error)",
                "Returns a fallback if the value is an error."),
    "IFNA": ("IFNA(value, value_if_na)",
             "Returns a fallback if the value is #N/A."),
    "INDEX": ("INDEX(array, row_num, [column_num])",
              "Value at a 1-based position inside a range."),
    "INT": ("INT(number)", "Rounds a number down to an integer."),
    "IRR": ("IRR(values, [guess])", "Internal rate of return of cash flows."),
    "ISBLANK": ("ISBLANK(value)", "True for empty cells."),
    "ISERROR": ("ISERROR(value)", "True for error values."),
    "ISNA": ("ISNA(value)", "True for the #N/A error value."),
    "ISNUMBER": ("ISNUMBER(value)", "True for numbers."),
    "ISTEXT": ("ISTEXT(value)", "True for text values."),
    "LARGE": ("LARGE(range, k)", "k-th largest value of a range."),
    "LCM": ("LCM(number1, [number2], ...)", "Least common multiple."),
    "LEFT": ("LEFT(text, [num_chars])", "First characters of a text."),
    "LEN": ("LEN(text)", "Number of characters of a text."),
    "LN": ("LN(number)", "Natural logarithm."),
    "LOG": ("LOG(number, [base])", "Logarithm to a given base."),
    "LOG10": ("LOG10(number)", "Logarithm to base 10."),
    "LOWER": ("LOWER(text)", "Converts text to lower case."),
    "MATCH": ("MATCH(value, range, [match_type])",
              "Position of a value inside a range."),
    "MAX": ("MAX(number1, [number2], ...)", "Largest number."),
    "MEDIAN": ("MEDIAN(number1, [number2], ...)", "Median of numbers."),
    "MID": ("MID(text, start_num, num_chars)", "Substring of a text."),
    "MIN": ("MIN(number1, [number2], ...)", "Smallest number."),
    "MINUTE": ("MINUTE(time)", "Minute of a time value."),
    "MOD": ("MOD(number, divisor)", "Remainder of a division."),
    "MONTH": ("MONTH(date)", "Month of a date."),
    "MROUND": ("MROUND(number, multiple)",
               "Rounds a number to the nearest multiple."),
    "NA": ("NA()", "The #N/A error value."),
    "NETWORKDAYS": ("NETWORKDAYS(start, end, [holidays])",
                    "Number of working days between two dates."),
    "NOT": ("NOT(logical)", "Inverts a logical value."),
    "NOW": ("NOW()", "Current date and time."),
    "NPER": ("NPER(rate, pmt, pv, [fv], [when])",
             "Number of periods of an investment."),
    "NPV": ("NPV(rate, value1, [value2], ...)", "Net present value."),
    "NUMBERVALUE": ("NUMBERVALUE(text)", "Converts text into a number."),
    "OR": ("OR(logical1, [logical2], ...)",
           "True if any argument is true."),
    "PI": ("PI()", "The constant pi."),
    "PMT": ("PMT(rate, nper, pv, [fv], [when])", "Periodic payment."),
    "POWER": ("POWER(number, power)", "Number raised to a power."),
    "PRODUCT": ("PRODUCT(number1, [number2], ...)",
                "Product of all numbers."),
    "PROPER": ("PROPER(text)", "Capitalizes each word of a text."),
    "PV": ("PV(rate, nper, pmt, [fv], [when])", "Present value."),
    "RAND": ("RAND()", "Random number between 0 and 1."),
    "RANDBETWEEN": ("RANDBETWEEN(bottom, top)",
                    "Random integer between two values."),
    "RANK": ("RANK(number, range, [order])",
             "Rank of a number inside a range."),
    "REPLACE": ("REPLACE(old_text, start_num, num_chars, new_text)",
                "Replaces characters by position."),
    "REPT": ("REPT(text, number_times)", "Repeats a text."),
    "RIGHT": ("RIGHT(text, [num_chars])", "Last characters of a text."),
    "ROUND": ("ROUND(number, [digits])", "Rounds half away from zero."),
    "ROUNDDOWN": ("ROUNDDOWN(number, [digits])",
                  "Rounds towards zero."),
    "ROUNDUP": ("ROUNDUP(number, [digits])", "Rounds away from zero."),
    "SEARCH": ("SEARCH(find_text, within_text, [start_num])",
               "Case insensitive text search."),
    "SECOND": ("SECOND(time)", "Second of a time value."),
    "SIGN": ("SIGN(number)", "Sign of a number."),
    "SMALL": ("SMALL(range, k)", "k-th smallest value of a range."),
    "SQRT": ("SQRT(number)", "Square root."),
    "STDEV": ("STDEV(number1, [number2], ...)",
              "Sample standard deviation."),
    "STDEVP": ("STDEVP(number1, [number2], ...)",
               "Population standard deviation."),
    "SUBSTITUTE": ("SUBSTITUTE(text, old, new, [instance_num])",
                   "Replaces occurrences of a text."),
    "SUM": ("SUM(number1, [number2], ...)", "Sums all numbers."),
    "SUMIF": ("SUMIF(range, criteria, [sum_range])",
              "Sums the values that match a criteria."),
    "SUMPRODUCT": ("SUMPRODUCT(range1, range2)",
                   "Sum of element wise products."),
    "SUMSQ": ("SUMSQ(number1, [number2], ...)", "Sum of squares."),
    "TEXT": ("TEXT(value, format_text)",
             "Formats a value, e.g. TEXT(1234.5, \"#,##0.00\")."),
    "TEXTJOIN": ("TEXTJOIN(delimiter, ignore_empty, text1, ...)",
                 "Joins texts with a delimiter."),
    "TIME": ("TIME(hour, minute, second)", "Builds a time value."),
    "TODAY": ("TODAY()", "Current date."),
    "TRIM": ("TRIM(text)", "Removes superfluous spaces."),
    "TRUE": ("TRUE()", "The logical value true."),
    "TRUNC": ("TRUNC(number, [digits])", "Truncates a number."),
    "UPPER": ("UPPER(text)", "Converts text to upper case."),
    "VALUE": ("VALUE(text)", "Converts text into a number."),
    "VAR": ("VAR(number1, [number2], ...)", "Sample variance."),
    "VARP": ("VARP(number1, [number2], ...)", "Population variance."),
    "VLOOKUP": ("VLOOKUP(value, table, col_index, [range_lookup])",
                "Searches the first column and returns a value to the right."),
    "WEEKDAY": ("WEEKDAY(date, [return_type])", "Day of the week."),
    "XOR": ("XOR(logical1, [logical2], ...)",
            "True for an odd number of true arguments."),
    "YEAR": ("YEAR(date)", "Year of a date."),
}
