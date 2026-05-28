import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# =====================================
# 데이터 경로 설정
# =====================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

USER_FILE = DATA_DIR / "user.txt"
PRODUCT_FILE = DATA_DIR / "product.txt"
ORDER_FILE = DATA_DIR / "order.txt"
ORDER_ITEM_FILE = DATA_DIR / "order_item.txt"
CATEGORY_FILE = DATA_DIR / "category.txt"
CART_FILE = DATA_DIR / "cart.txt"
CART_ITEM_FILE = DATA_DIR / "cart_item.txt"
COUPON_FILE = DATA_DIR / "coupon.txt"
USER_COUPON_FILE = DATA_DIR / "user_coupon.txt"
PRODUCT_CATEGORY_FILE = DATA_DIR / "product_category.txt"
VIRTUAL_TIME_FILE = DATA_DIR / "virtual_time.txt"

ALL_FILES = [
    USER_FILE,
    PRODUCT_FILE,
    ORDER_FILE,
    ORDER_ITEM_FILE,
    CATEGORY_FILE,
    CART_FILE,
    CART_ITEM_FILE,
    COUPON_FILE,
    USER_COUPON_FILE,
    PRODUCT_CATEGORY_FILE,
    VIRTUAL_TIME_FILE,
]


# =====================================
# 초기 데이터
# =====================================
DEFAULT_ADMIN_RECORD = "1|admin|1234|관리자|ADMIN"

DEFAULT_CATEGORY_RECORDS = [
    "1|식품|0",
    "2|과일|1",
    "3|음료|1",
    "4|생활용품|0",
    "5|세제|4",
    "6|욕실용품|4",
    "7|주방용품|0",
    "8|조리도구|7",
    "9|식기|7",
    "10|전자제품|0",
    "11|노트북|10",
    "12|마우스|10",
    "13|키보드|10",
    "14|문구|0",
    "15|필기구|14",
    "16|노트|14",
    "17|의류|0",
    "18|상의|17",
    "19|하의|17",
    "20|기타|0",
]

DEFAULT_COUPON_RECORDS = [
    "1|신규 회원 할인 쿠폰|FIXED|5000|ALL|0|10000|30|SIGNUP|0",
    "2|주문 감사 쿠폰|RATE|10|ALL|0|30000|14|ORDER_COUNT|3",
]

ORDER_STATUSES = {
    "PENDING",
    "ACCEPTED",
    "REJECTED",
    "CANCEL_REQUESTED",
    "CANCELLED",
}


# =====================================
# 공통 유틸
# =====================================
def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_file_exists(file_path: Path) -> None:
    if not file_path.exists():
        file_path.write_text("", encoding="utf-8")


def read_lines(file_path: Path) -> list[str]:
    if not file_path.exists():
        return []

    return file_path.read_text(encoding="utf-8").splitlines()


def write_lines(file_path: Path, lines: list[str]) -> None:
    if lines:
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        file_path.write_text("", encoding="utf-8")


def normalize_text(value: str) -> str:
    return value.strip()


def split_record(line: str, expected_count: int) -> list[str] | None:
    parts = line.split("|")
    if len(parts) != expected_count:
        return None
    return parts


def serialize_record(values: list[str]) -> str:
    return "|".join(values)


def format_money(value: int) -> str:
    return f"{value:,}원"


def get_display_width(value: str) -> int:
    width = 0
    for char in value:
        width += 2 if ord(char) > 127 else 1
    return width


def pad_display_text(value: str, width: int) -> str:
    return value + " " * max(width - get_display_width(value), 0)


# =====================================
# 정규화 / 검증 함수
# =====================================
def is_valid_numeric_id(value: str) -> bool:
    value = normalize_text(value)
    if value == "":
        return False
    if not value.isdigit():
        return False
    if len(value) > 1 and value.startswith("0"):
        return False
    return int(value) > 0


def is_valid_zero_or_numeric_id(value: str) -> bool:
    value = normalize_text(value)
    return value == "0" or is_valid_numeric_id(value)


def is_valid_login_id(value: str) -> bool:
    value = normalize_text(value)
    return bool(2 <= len(value) <= 10 and re.fullmatch(r"[A-Za-z0-9]+", value))


def is_valid_password(value: str) -> bool:
    value = normalize_text(value)
    return bool(2 <= len(value) <= 10 and re.fullmatch(r"[A-Za-z0-9]+", value))


def is_valid_name(value: str) -> bool:
    value = normalize_text(value)
    return bool(1 <= len(value) <= 4 and re.fullmatch(r"[가-힣]+", value))


def is_valid_role(value: str) -> bool:
    return normalize_text(value) in {"USER", "ADMIN"}


def is_valid_category_name_text(value: str) -> bool:
    value = normalize_text(value)
    return bool(1 <= len(value) <= 10 and re.fullmatch(r"[가-힣]+", value))


def has_forbidden_separator(value: str) -> bool:
    return any(separator in value for separator in "|%&")


def is_valid_product_name(value: str) -> bool:
    value = normalize_text(value)
    return bool(1 <= len(value) <= 20 and not has_forbidden_separator(value))


def is_valid_coupon_name(value: str) -> bool:
    value = normalize_text(value)
    return bool(1 <= len(value) <= 30 and not has_forbidden_separator(value))


def is_valid_nonnegative_amount(value: str) -> bool:
    value = normalize_text(value)
    if value == "":
        return False
    if not value.isdigit():
        return False
    if len(value) > 1 and value.startswith("0"):
        return False
    return int(value) >= 0


def is_valid_price(value: str) -> bool:
    if not is_valid_numeric_id(value):
        return False
    return 1 <= int(normalize_text(value)) <= 1_000_000


def is_valid_stock(value: str) -> bool:
    return is_valid_nonnegative_amount(value)


def is_valid_quantity(value: str) -> bool:
    if not is_valid_numeric_id(value):
        return False
    return int(normalize_text(value)) >= 1


def is_valid_order_status(value: str) -> bool:
    return normalize_text(value) in ORDER_STATUSES


def is_valid_virtual_time(value: str) -> bool:
    value = normalize_text(value)
    if len(value) != 12:
        return False
    if not value.isdigit():
        return False

    try:
        datetime.strptime(value, "%y%m%d%H%M%S")
        return True
    except ValueError:
        return False


def is_valid_order_time(value: str) -> bool:
    return is_valid_virtual_time(value)


def is_valid_discount_type(value: str) -> bool:
    return normalize_text(value) in {"FIXED", "RATE"}


def is_valid_target_type(value: str) -> bool:
    return normalize_text(value) in {"ALL", "PRODUCT", "CATEGORY"}


def is_valid_issue_type(value: str) -> bool:
    return normalize_text(value) in {"SIGNUP", "ORDER_COUNT"}


def is_valid_used_status(value: str) -> bool:
    return normalize_text(value) in {"UNUSED", "USED"}


# =====================================
# 초기화 / 레거시 데이터 보정
# =====================================
def initialize_user_file() -> None:
    lines = [line for line in read_lines(USER_FILE) if normalize_text(line) != ""]
    if not lines:
        write_lines(USER_FILE, [DEFAULT_ADMIN_RECORD])


def initialize_category_file() -> None:
    lines = [line for line in read_lines(CATEGORY_FILE) if normalize_text(line) != ""]
    valid_records = [parse_category_record(line) for line in lines]

    if not lines or all(record is None for record in valid_records):
        write_lines(CATEGORY_FILE, DEFAULT_CATEGORY_RECORDS)


def initialize_coupon_file() -> None:
    lines = [line for line in read_lines(COUPON_FILE) if normalize_text(line) != ""]
    if not lines:
        write_lines(COUPON_FILE, DEFAULT_COUPON_RECORDS)


def migrate_legacy_product_file() -> None:
    lines = read_lines(PRODUCT_FILE)
    categories = load_categories()
    valid_category_ids = {category["category_id"] for category in categories}
    products = []
    product_categories = load_product_categories([], categories, validate_products=False)
    changed = False

    for line in lines:
        if normalize_text(line) == "":
            continue

        parts = line.split("|")
        if len(parts) == 5:
            product_id, category_id, product_name, price, stock = parts
            if (
                is_valid_numeric_id(product_id)
                and normalize_text(category_id) in valid_category_ids
                and is_valid_product_name(product_name)
                and is_valid_price(price)
                and is_valid_stock(stock)
            ):
                products.append(
                    {
                        "product_id": normalize_text(product_id),
                        "product_name": normalize_text(product_name),
                        "price": normalize_text(price),
                        "stock": normalize_text(stock),
                    }
                )
                product_categories.append(
                    {
                        "product_id": normalize_text(product_id),
                        "category_id": normalize_text(category_id),
                    }
                )
                changed = True
            continue

        record = parse_product_record(line)
        if record is not None:
            products.append(record)

    if changed:
        save_products(deduplicate_products(products))
        save_product_categories(product_categories)


def initialize_data_files() -> None:
    ensure_data_dir()

    for file_path in ALL_FILES:
        ensure_file_exists(file_path)

    initialize_category_file()
    initialize_user_file()
    initialize_coupon_file()
    migrate_legacy_product_file()


def print_initialization_result() -> None:
    print("데이터 파일 초기화가 완료되었습니다.")
    print(f"데이터 폴더: {DATA_DIR}")
    print("생성/확인 대상 파일:")
    for file_path in ALL_FILES:
        print(f"- {file_path.name}")


# =====================================
# 레코드 파싱 함수
# =====================================
def parse_user_record(line: str) -> dict | None:
    parts = split_record(line, 5)
    if parts is None:
        return None

    user_id, login_id, password, name, role = parts

    if not is_valid_numeric_id(user_id):
        return None
    if not is_valid_login_id(login_id):
        return None
    if not is_valid_password(password):
        return None
    if not is_valid_name(name):
        return None
    if not is_valid_role(role):
        return None

    return {
        "user_id": normalize_text(user_id),
        "login_id": normalize_text(login_id),
        "password": normalize_text(password),
        "name": normalize_text(name),
        "role": normalize_text(role),
    }


def parse_product_record(line: str) -> dict | None:
    parts = split_record(line, 4)
    if parts is None:
        return None

    product_id, product_name, price, stock = parts

    if not is_valid_numeric_id(product_id):
        return None
    if not is_valid_product_name(product_name):
        return None
    if not is_valid_price(price):
        return None
    if not is_valid_stock(stock):
        return None

    return {
        "product_id": normalize_text(product_id),
        "product_name": normalize_text(product_name),
        "price": normalize_text(price),
        "stock": normalize_text(stock),
    }


def parse_category_record(line: str) -> dict | None:
    parts = split_record(line, 3)
    if parts is None:
        return None

    category_id, category_name, parent_category_id = parts

    if not is_valid_numeric_id(category_id):
        return None
    if not is_valid_category_name_text(category_name):
        return None
    if not is_valid_zero_or_numeric_id(parent_category_id):
        return None

    return {
        "category_id": normalize_text(category_id),
        "category_name": normalize_text(category_name),
        "parent_category_id": normalize_text(parent_category_id),
    }


def parse_product_category_record(line: str) -> dict | None:
    parts = split_record(line, 2)
    if parts is None:
        return None

    product_id, category_id = parts
    if not is_valid_numeric_id(product_id):
        return None
    if not is_valid_numeric_id(category_id):
        return None

    return {
        "product_id": normalize_text(product_id),
        "category_id": normalize_text(category_id),
    }


def parse_cart_record(line: str) -> dict | None:
    parts = split_record(line, 2)
    if parts is None:
        return None

    cart_id, user_id = parts
    if not is_valid_numeric_id(cart_id):
        return None
    if not is_valid_numeric_id(user_id):
        return None

    return {
        "cart_id": normalize_text(cart_id),
        "user_id": normalize_text(user_id),
    }


def parse_cart_item_record(line: str) -> dict | None:
    parts = split_record(line, 4)
    if parts is None:
        return None

    cart_item_id, cart_id, product_id, quantity = parts
    if not is_valid_numeric_id(cart_item_id):
        return None
    if not is_valid_numeric_id(cart_id):
        return None
    if not is_valid_numeric_id(product_id):
        return None
    if not is_valid_quantity(quantity):
        return None

    return {
        "cart_item_id": normalize_text(cart_item_id),
        "cart_id": normalize_text(cart_id),
        "product_id": normalize_text(product_id),
        "quantity": normalize_text(quantity),
    }


def parse_order_record(line: str) -> dict | None:
    parts = line.split("|")

    if len(parts) == 5:
        order_id, user_id, total_price, order_status, order_time = parts
        parts = [
            order_id,
            user_id,
            total_price,
            "0",
            total_price,
            order_status,
            order_time,
            "0",
        ]

    if len(parts) != 8:
        return None

    (
        order_id,
        user_id,
        original_price,
        discount_price,
        total_price,
        order_status,
        order_time,
        user_coupon_id,
    ) = parts

    if not is_valid_numeric_id(order_id):
        return None
    if not is_valid_numeric_id(user_id):
        return None
    if not is_valid_price(original_price):
        return None
    if not is_valid_nonnegative_amount(discount_price):
        return None
    if not is_valid_nonnegative_amount(total_price):
        return None
    if int(discount_price) > int(original_price):
        return None
    if int(total_price) != int(original_price) - int(discount_price):
        return None
    if not is_valid_order_status(order_status):
        return None
    if not is_valid_virtual_time(order_time):
        return None
    if not is_valid_zero_or_numeric_id(user_coupon_id):
        return None

    return {
        "order_id": normalize_text(order_id),
        "user_id": normalize_text(user_id),
        "original_price": normalize_text(original_price),
        "discount_price": normalize_text(discount_price),
        "total_price": normalize_text(total_price),
        "order_status": normalize_text(order_status),
        "order_time": normalize_text(order_time),
        "user_coupon_id": normalize_text(user_coupon_id),
    }


def parse_order_item_record(line: str) -> dict | None:
    parts = split_record(line, 6)
    if parts is None:
        return None

    order_item_id, order_id, product_id, product_name, price, quantity = parts
    if not is_valid_numeric_id(order_item_id):
        return None
    if not is_valid_numeric_id(order_id):
        return None
    if not is_valid_numeric_id(product_id):
        return None
    if not is_valid_product_name(product_name):
        return None
    if not is_valid_price(price):
        return None
    if not is_valid_quantity(quantity):
        return None

    return {
        "order_item_id": normalize_text(order_item_id),
        "order_id": normalize_text(order_id),
        "product_id": normalize_text(product_id),
        "product_name": normalize_text(product_name),
        "price": normalize_text(price),
        "quantity": normalize_text(quantity),
    }


def parse_coupon_record(line: str) -> dict | None:
    parts = split_record(line, 10)
    if parts is None:
        return None

    (
        coupon_id,
        coupon_name,
        discount_type,
        discount_value,
        target_type,
        target_id,
        min_order_price,
        valid_days,
        issue_type,
        issue_threshold,
    ) = parts

    discount_type = normalize_text(discount_type)
    target_type = normalize_text(target_type)
    issue_type = normalize_text(issue_type)
    target_id = normalize_text(target_id)
    issue_threshold = normalize_text(issue_threshold)

    if not is_valid_numeric_id(coupon_id):
        return None
    if not is_valid_coupon_name(coupon_name):
        return None
    if not is_valid_discount_type(discount_type):
        return None
    if not is_valid_numeric_id(discount_value):
        return None
    if discount_type == "RATE" and not (1 <= int(discount_value) <= 100):
        return None
    if not is_valid_target_type(target_type):
        return None
    if target_type == "ALL":
        if target_id != "0":
            return None
    elif not is_valid_numeric_id(target_id):
        return None
    if not is_valid_nonnegative_amount(min_order_price):
        return None
    if not is_valid_numeric_id(valid_days):
        return None
    if not is_valid_issue_type(issue_type):
        return None
    if issue_type == "SIGNUP":
        if issue_threshold != "0":
            return None
    elif not is_valid_numeric_id(issue_threshold):
        return None

    return {
        "coupon_id": normalize_text(coupon_id),
        "coupon_name": normalize_text(coupon_name),
        "discount_type": discount_type,
        "discount_value": normalize_text(discount_value),
        "target_type": target_type,
        "target_id": target_id,
        "min_order_price": normalize_text(min_order_price),
        "valid_days": normalize_text(valid_days),
        "issue_type": issue_type,
        "issue_threshold": issue_threshold,
    }


def parse_user_coupon_record(line: str) -> dict | None:
    parts = split_record(line, 6)
    if parts is None:
        return None

    user_coupon_id, user_id, coupon_id, issued_at, expires_at, used_status = parts

    if not is_valid_numeric_id(user_coupon_id):
        return None
    if not is_valid_numeric_id(user_id):
        return None
    if not is_valid_numeric_id(coupon_id):
        return None
    if not is_valid_virtual_time(issued_at):
        return None
    if not is_valid_virtual_time(expires_at):
        return None
    if normalize_text(issued_at) > normalize_text(expires_at):
        return None
    if not is_valid_used_status(used_status):
        return None

    return {
        "user_coupon_id": normalize_text(user_coupon_id),
        "user_id": normalize_text(user_id),
        "coupon_id": normalize_text(coupon_id),
        "issued_at": normalize_text(issued_at),
        "expires_at": normalize_text(expires_at),
        "used_status": normalize_text(used_status),
    }


# =====================================
# 중복 제거 / ID 생성 함수
# =====================================
def get_next_numeric_id(records: list[dict], key: str) -> str:
    if not records:
        return "1"
    return str(max(int(record[key]) for record in records) + 1)


def get_next_user_id(users: list[dict]) -> str:
    return get_next_numeric_id(users, "user_id")


def get_next_product_id(products: list[dict]) -> str:
    return get_next_numeric_id(products, "product_id")


def get_next_category_id(categories: list[dict]) -> str:
    return get_next_numeric_id(categories, "category_id")


def get_next_cart_id(carts: list[dict]) -> str:
    return get_next_numeric_id(carts, "cart_id")


def get_next_cart_item_id(cart_items: list[dict], cart_id: str) -> str:
    same_cart_items = [item for item in cart_items if item["cart_id"] == cart_id]
    if not same_cart_items:
        return "1"
    return str(max(int(item["cart_item_id"]) for item in same_cart_items) + 1)


def get_next_order_id(orders: list[dict]) -> str:
    return get_next_numeric_id(orders, "order_id")


def get_next_order_item_id(order_items: list[dict]) -> str:
    return get_next_numeric_id(order_items, "order_item_id")


def get_next_user_coupon_id(user_coupons: list[dict]) -> str:
    return get_next_numeric_id(user_coupons, "user_coupon_id")


def deduplicate_by_key(records: list[dict], key: str) -> list[dict]:
    result = []
    seen = set()
    for record in records:
        value = record[key]
        if value in seen:
            continue
        seen.add(value)
        result.append(record)
    return result


def deduplicate_users(users: list[dict]) -> list[dict]:
    result = []
    seen_user_ids = set()
    seen_login_ids = set()
    for user in users:
        user_id = user["user_id"]
        login_id = user["login_id"].upper()
        if user_id in seen_user_ids or login_id in seen_login_ids:
            continue
        seen_user_ids.add(user_id)
        seen_login_ids.add(login_id)
        result.append(user)
    return result


def deduplicate_products(products: list[dict]) -> list[dict]:
    return deduplicate_by_key(products, "product_id")


def deduplicate_categories(categories: list[dict]) -> list[dict]:
    return deduplicate_by_key(categories, "category_id")


def deduplicate_product_categories(product_categories: list[dict]) -> list[dict]:
    result = []
    seen_pairs = set()
    for item in product_categories:
        key = (item["product_id"], item["category_id"])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        result.append(item)
    return result


def deduplicate_carts(carts: list[dict]) -> list[dict]:
    result = []
    seen_cart_ids = set()
    seen_user_ids = set()
    for cart in carts:
        if cart["cart_id"] in seen_cart_ids or cart["user_id"] in seen_user_ids:
            continue
        seen_cart_ids.add(cart["cart_id"])
        seen_user_ids.add(cart["user_id"])
        result.append(cart)
    return result


def deduplicate_cart_items(cart_items: list[dict]) -> list[dict]:
    result = []
    seen_pairs = set()
    for item in cart_items:
        key = (item["cart_id"], item["cart_item_id"])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        result.append(item)
    return result


def deduplicate_orders(orders: list[dict]) -> list[dict]:
    return deduplicate_by_key(orders, "order_id")


def deduplicate_order_items(order_items: list[dict]) -> list[dict]:
    return deduplicate_by_key(order_items, "order_item_id")


def deduplicate_coupons(coupons: list[dict]) -> list[dict]:
    return deduplicate_by_key(coupons, "coupon_id")


def deduplicate_user_coupons(user_coupons: list[dict]) -> list[dict]:
    return deduplicate_by_key(user_coupons, "user_coupon_id")


# =====================================
# 파일 로드 함수
# =====================================
def load_users() -> list[dict]:
    users = []
    for line in read_lines(USER_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_user_record(line)
        if record is not None:
            users.append(record)
    return deduplicate_users(users)


def load_products() -> list[dict]:
    products = []
    for line in read_lines(PRODUCT_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_product_record(line)
        if record is not None:
            products.append(record)
    return sorted(deduplicate_products(products), key=lambda product: int(product["product_id"]))


def load_categories() -> list[dict]:
    categories = []
    for line in read_lines(CATEGORY_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_category_record(line)
        if record is not None:
            categories.append(record)

    categories = deduplicate_categories(categories)
    valid_category_ids = {category["category_id"] for category in categories}
    filtered = []
    for category in categories:
        parent_id = category["parent_category_id"]
        if parent_id != "0" and parent_id not in valid_category_ids:
            continue
        if parent_id == category["category_id"]:
            continue
        filtered.append(category)

    return sorted(filtered, key=lambda category: int(category["category_id"]))


def load_product_categories(
    products: list[dict] | None = None,
    categories: list[dict] | None = None,
    *,
    validate_products: bool = True,
) -> list[dict]:
    if products is None:
        products = load_products()
    if categories is None:
        categories = load_categories()

    valid_product_ids = {product["product_id"] for product in products}
    valid_category_ids = {category["category_id"] for category in categories}

    product_categories = []
    for line in read_lines(PRODUCT_CATEGORY_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_product_category_record(line)
        if record is None:
            continue
        if validate_products and record["product_id"] not in valid_product_ids:
            continue
        if record["category_id"] not in valid_category_ids:
            continue
        product_categories.append(record)

    product_categories = deduplicate_product_categories(product_categories)
    return sorted(
        product_categories,
        key=lambda item: (int(item["product_id"]), int(item["category_id"])),
    )


def load_carts(users: list[dict] | None = None) -> list[dict]:
    carts = []
    for line in read_lines(CART_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_cart_record(line)
        if record is not None:
            carts.append(record)

    carts = deduplicate_carts(carts)
    if users is not None:
        valid_user_ids = {user["user_id"] for user in users}
        carts = [cart for cart in carts if cart["user_id"] in valid_user_ids]
    return carts


def merge_duplicate_cart_products(cart_items: list[dict]) -> tuple[list[dict], bool]:
    merged = {}
    duplicate_found = False
    for item in cart_items:
        key = (item["cart_id"], item["product_id"])
        if key not in merged:
            merged[key] = item.copy()
        else:
            duplicate_found = True
            merged[key]["quantity"] = str(
                int(merged[key]["quantity"]) + int(item["quantity"])
            )
    return list(merged.values()), duplicate_found


def load_cart_items(
    carts: list[dict] | None = None,
    products: list[dict] | None = None,
) -> list[dict]:
    cart_items = []
    for line in read_lines(CART_ITEM_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_cart_item_record(line)
        if record is not None:
            cart_items.append(record)

    cart_items = deduplicate_cart_items(cart_items)
    if carts is not None and products is not None:
        valid_cart_ids = {cart["cart_id"] for cart in carts}
        valid_product_ids = {product["product_id"] for product in products}
        cart_items = [
            item
            for item in cart_items
            if item["cart_id"] in valid_cart_ids and item["product_id"] in valid_product_ids
        ]
        cart_items, duplicate_found = merge_duplicate_cart_products(cart_items)
        if duplicate_found:
            print("[WARNING] 동일 장바구니 내 중복 상품이 발견되어 수량을 합산하였습니다.")

    return cart_items


def load_orders() -> list[dict]:
    users = load_users()
    valid_user_ids = {user["user_id"] for user in users}
    orders = []
    for line in read_lines(ORDER_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_order_record(line)
        if record is not None and record["user_id"] in valid_user_ids:
            orders.append(record)
    return sorted(deduplicate_orders(orders), key=lambda order: int(order["order_id"]))


def load_order_items() -> list[dict]:
    orders = load_orders()
    valid_order_ids = {order["order_id"] for order in orders}
    order_items = []
    for line in read_lines(ORDER_ITEM_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_order_item_record(line)
        if record is not None and record["order_id"] in valid_order_ids:
            order_items.append(record)
    return sorted(
        deduplicate_order_items(order_items),
        key=lambda item: int(item["order_item_id"]),
    )


def load_coupons() -> list[dict]:
    products = load_products()
    categories = load_categories()
    valid_product_ids = {product["product_id"] for product in products}
    valid_category_ids = {category["category_id"] for category in categories}
    coupons = []

    for line in read_lines(COUPON_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_coupon_record(line)
        if record is None:
            continue
        if record["target_type"] == "PRODUCT" and record["target_id"] not in valid_product_ids:
            continue
        if record["target_type"] == "CATEGORY" and record["target_id"] not in valid_category_ids:
            continue
        coupons.append(record)

    return sorted(deduplicate_coupons(coupons), key=lambda coupon: int(coupon["coupon_id"]))


def load_user_coupons(
    users: list[dict] | None = None,
    coupons: list[dict] | None = None,
) -> list[dict]:
    if users is None:
        users = load_users()
    if coupons is None:
        coupons = load_coupons()

    valid_user_ids = {user["user_id"] for user in users}
    valid_coupon_ids = {coupon["coupon_id"] for coupon in coupons}
    user_coupons = []

    for line in read_lines(USER_COUPON_FILE):
        if normalize_text(line) == "":
            continue
        record = parse_user_coupon_record(line)
        if record is None:
            continue
        if record["user_id"] not in valid_user_ids:
            continue
        if record["coupon_id"] not in valid_coupon_ids:
            continue
        user_coupons.append(record)

    return sorted(
        deduplicate_user_coupons(user_coupons),
        key=lambda user_coupon: int(user_coupon["user_coupon_id"]),
    )


# =====================================
# 파일 저장 함수
# =====================================
def save_users(users: list[dict]) -> None:
    lines = [
        serialize_record(
            [
                user["user_id"],
                user["login_id"],
                user["password"],
                user["name"],
                user["role"],
            ]
        )
        for user in users
    ]
    write_lines(USER_FILE, lines)


def save_products(products: list[dict]) -> None:
    lines = []
    for product in sorted(products, key=lambda item: int(item["product_id"])):
        lines.append(
            serialize_record(
                [
                    product["product_id"],
                    product["product_name"],
                    product["price"],
                    product["stock"],
                ]
            )
        )
    write_lines(PRODUCT_FILE, lines)


def save_categories(categories: list[dict]) -> None:
    lines = []
    for category in sorted(categories, key=lambda item: int(item["category_id"])):
        lines.append(
            serialize_record(
                [
                    category["category_id"],
                    category["category_name"],
                    category["parent_category_id"],
                ]
            )
        )
    write_lines(CATEGORY_FILE, lines)


def save_product_categories(product_categories: list[dict]) -> None:
    product_categories = deduplicate_product_categories(product_categories)
    lines = []
    for item in sorted(
        product_categories,
        key=lambda record: (int(record["product_id"]), int(record["category_id"])),
    ):
        lines.append(serialize_record([item["product_id"], item["category_id"]]))
    write_lines(PRODUCT_CATEGORY_FILE, lines)


def save_carts(carts: list[dict]) -> None:
    lines = [serialize_record([cart["cart_id"], cart["user_id"]]) for cart in carts]
    write_lines(CART_FILE, lines)


def save_cart_items(cart_items: list[dict]) -> None:
    lines = [
        serialize_record(
            [
                item["cart_item_id"],
                item["cart_id"],
                item["product_id"],
                item["quantity"],
            ]
        )
        for item in cart_items
    ]
    write_lines(CART_ITEM_FILE, lines)


def save_orders(orders: list[dict]) -> None:
    lines = [
        serialize_record(
            [
                order["order_id"],
                order["user_id"],
                order["original_price"],
                order["discount_price"],
                order["total_price"],
                order["order_status"],
                order["order_time"],
                order["user_coupon_id"],
            ]
        )
        for order in orders
    ]
    write_lines(ORDER_FILE, lines)


def save_order_items(order_items: list[dict]) -> None:
    lines = [
        serialize_record(
            [
                item["order_item_id"],
                item["order_id"],
                item["product_id"],
                item["product_name"],
                item["price"],
                item["quantity"],
            ]
        )
        for item in order_items
    ]
    write_lines(ORDER_ITEM_FILE, lines)


def save_user_coupons(user_coupons: list[dict]) -> None:
    lines = []
    for user_coupon in sorted(user_coupons, key=lambda item: int(item["user_coupon_id"])):
        required_keys = {
            "user_coupon_id",
            "user_id",
            "coupon_id",
            "issued_at",
            "expires_at",
            "used_status",
        }
        if not required_keys.issubset(user_coupon.keys()):
            continue
        lines.append(
            serialize_record(
                [
                    user_coupon["user_coupon_id"],
                    user_coupon["user_id"],
                    user_coupon["coupon_id"],
                    user_coupon["issued_at"],
                    user_coupon["expires_at"],
                    user_coupon["used_status"],
                ]
            )
        )
    write_lines(USER_COUPON_FILE, lines)


# =====================================
# 기본 조회 함수
# =====================================
def find_user_by_user_id(users: list[dict], user_id: str) -> dict | None:
    user_id = normalize_text(user_id)
    for user in users:
        if user["user_id"] == user_id:
            return user
    return None


def find_user_by_login_id(users: list[dict], login_id: str) -> dict | None:
    login_id = normalize_text(login_id).upper()
    for user in users:
        if user["login_id"].upper() == login_id:
            return user
    return None


def find_product_by_product_id(products: list[dict], product_id: str) -> dict | None:
    product_id = normalize_text(product_id)
    for product in products:
        if product["product_id"] == product_id:
            return product
    return None


def find_product_by_name(products: list[dict], product_name: str) -> dict | None:
    target = normalize_text(product_name)
    for product in products:
        if product["product_name"] == target:
            return product
    return None


def find_category_by_id(categories: list[dict], category_id: str) -> dict | None:
    category_id = normalize_text(category_id)
    for category in categories:
        if category["category_id"] == category_id:
            return category
    return None


def find_cart_by_user_id(carts: list[dict], user_id: str) -> dict | None:
    user_id = normalize_text(user_id)
    for cart in carts:
        if cart["user_id"] == user_id:
            return cart
    return None


def find_order_by_order_id(orders: list[dict], order_id: str) -> dict | None:
    order_id = normalize_text(order_id)
    for order in orders:
        if order["order_id"] == order_id:
            return order
    return None


def find_coupon_by_coupon_id(coupons: list[dict], coupon_id: str) -> dict | None:
    coupon_id = normalize_text(coupon_id)
    for coupon in coupons:
        if coupon["coupon_id"] == coupon_id:
            return coupon
    return None


def find_user_coupon_by_id(user_coupons: list[dict], user_coupon_id: str) -> dict | None:
    user_coupon_id = normalize_text(user_coupon_id)
    for user_coupon in user_coupons:
        if user_coupon["user_coupon_id"] == user_coupon_id:
            return user_coupon
    return None


def get_order_items_by_order_id(order_items: list[dict], order_id: str) -> list[dict]:
    order_id = normalize_text(order_id)
    return [item for item in order_items if item["order_id"] == order_id]


def build_category_name_map(categories: list[dict]) -> dict[str, str]:
    return {category["category_id"]: category["category_name"] for category in categories}


def get_category_descendant_ids(category_id: str, categories: list[dict]) -> set[str]:
    category_id = normalize_text(category_id)
    if find_category_by_id(categories, category_id) is None:
        return set()

    children_by_parent: dict[str, list[str]] = defaultdict(list)
    for category in categories:
        children_by_parent[category["parent_category_id"]].append(category["category_id"])

    result = set()
    stack = [category_id]
    while stack:
        current_id = stack.pop()
        if current_id in result:
            continue
        result.add(current_id)
        stack.extend(children_by_parent.get(current_id, []))
    return result


def get_product_category_names(
    product_id: str,
    product_categories: list[dict],
    categories: list[dict],
) -> str:
    category_name_map = build_category_name_map(categories)
    category_ids = sorted(
        {
            item["category_id"]
            for item in product_categories
            if item["product_id"] == normalize_text(product_id)
        },
        key=int,
    )
    names = [
        category_name_map[category_id]
        for category_id in category_ids
        if category_id in category_name_map
    ]
    return ", ".join(names) if names else "미분류"


# =====================================
# 사용자 서비스 함수
# =====================================
def create_user(login_id: str, password: str, name: str) -> dict:
    users = load_users()
    if not is_valid_login_id(login_id):
        raise ValueError("로그인 ID 형식이 올바르지 않습니다.")
    if not is_valid_password(password):
        raise ValueError("비밀번호 형식이 올바르지 않습니다.")
    if not is_valid_name(name):
        raise ValueError("이름 형식이 올바르지 않습니다.")
    if find_user_by_login_id(users, login_id) is not None:
        raise ValueError("이미 존재하는 로그인 ID입니다.")

    user = {
        "user_id": get_next_user_id(users),
        "login_id": normalize_text(login_id),
        "password": normalize_text(password),
        "name": normalize_text(name),
        "role": "USER",
    }
    users.append(user)
    save_users(users)
    return user


def authenticate_user(login_id: str, password: str) -> dict | None:
    if not is_valid_login_id(login_id) or not is_valid_password(password):
        return None

    user = find_user_by_login_id(load_users(), login_id)
    if user is None:
        return None
    if user["password"] != normalize_text(password):
        return None
    return user


# =====================================
# 상품 / 카테고리 서비스 함수
# =====================================
def parse_category_id_list(input_text: str, categories: list[dict]) -> list[str]:
    input_text = normalize_text(input_text)
    if input_text == "":
        raise ValueError("카테고리를 1개 이상 입력하세요.")

    tokens = [token.strip() for token in input_text.split(",")]
    if any(token == "" for token in tokens):
        raise ValueError("오류 : 올바른 ID 값을 입력해주세요.")

    valid_category_ids = {category["category_id"] for category in categories}
    result = []
    seen = set()
    for token in tokens:
        if not is_valid_numeric_id(token):
            raise ValueError("오류 : 올바른 ID 값을 입력해주세요.")
        if token not in valid_category_ids:
            raise ValueError("오류 : 등록되지 않은 카테고리 ID입니다.")
        if token in seen:
            raise ValueError("오류 : 동일한 카테고리를 중복 입력할 수 없습니다.")
        seen.add(token)
        result.append(token)
    return result


def create_product(
    category_ids: list[str],
    product_name: str,
    price: str,
    stock: str,
) -> dict:
    products = load_products()
    categories = load_categories()
    valid_category_ids = {category["category_id"] for category in categories}

    if not category_ids:
        raise ValueError("카테고리를 1개 이상 입력하세요.")
    if any(category_id not in valid_category_ids for category_id in category_ids):
        raise ValueError("등록되지 않은 카테고리 ID입니다.")
    if not is_valid_product_name(product_name):
        raise ValueError("상품명 형식이 올바르지 않습니다.")
    if not is_valid_price(price):
        raise ValueError("가격 형식이 올바르지 않습니다.")
    if not is_valid_stock(stock):
        raise ValueError("재고 형식이 올바르지 않습니다.")
    if find_product_by_name(products, product_name) is not None:
        raise ValueError("이미 존재하는 상품명입니다.")

    product = {
        "product_id": get_next_product_id(products),
        "product_name": normalize_text(product_name),
        "price": normalize_text(price),
        "stock": normalize_text(stock),
    }
    products.append(product)

    product_categories = load_product_categories(products, categories)
    for category_id in category_ids:
        product_categories.append(
            {
                "product_id": product["product_id"],
                "category_id": normalize_text(category_id),
            }
        )

    save_products(products)
    save_product_categories(product_categories)
    return product


def update_product(
    product_id: str,
    *,
    new_product_name: str | None = None,
    new_price: str | None = None,
    new_stock: str | None = None,
) -> dict:
    products = load_products()
    product = find_product_by_product_id(products, product_id)
    if product is None:
        raise ValueError("존재하지 않는 상품입니다.")

    if new_product_name is not None:
        if not is_valid_product_name(new_product_name):
            raise ValueError("상품명 형식이 올바르지 않습니다.")
        other = find_product_by_name(products, new_product_name)
        if other is not None and other["product_id"] != product["product_id"]:
            raise ValueError("이미 존재하는 상품명입니다.")
        product["product_name"] = normalize_text(new_product_name)

    if new_price is not None:
        if not is_valid_price(new_price):
            raise ValueError("가격 형식이 올바르지 않습니다.")
        product["price"] = normalize_text(new_price)

    if new_stock is not None:
        if not is_valid_stock(new_stock):
            raise ValueError("재고 형식이 올바르지 않습니다.")
        product["stock"] = normalize_text(new_stock)

    save_products(products)
    return product


def update_product_categories(product_id: str, category_ids: list[str]) -> None:
    products = load_products()
    categories = load_categories()
    product = find_product_by_product_id(products, product_id)
    if product is None:
        raise ValueError("존재하지 않는 상품입니다.")
    if not category_ids:
        raise ValueError("카테고리를 1개 이상 입력하세요.")

    valid_category_ids = {category["category_id"] for category in categories}
    if any(category_id not in valid_category_ids for category_id in category_ids):
        raise ValueError("등록되지 않은 카테고리 ID입니다.")

    product_categories = load_product_categories(products, categories)
    product_categories = [
        item for item in product_categories if item["product_id"] != normalize_text(product_id)
    ]
    for category_id in category_ids:
        product_categories.append(
            {
                "product_id": normalize_text(product_id),
                "category_id": normalize_text(category_id),
            }
        )
    save_product_categories(product_categories)


def has_sibling_category_name(
    categories: list[dict],
    category_name: str,
    parent_category_id: str,
    *,
    except_category_id: str | None = None,
) -> bool:
    category_name = normalize_text(category_name)
    parent_category_id = normalize_text(parent_category_id)
    for category in categories:
        if except_category_id is not None and category["category_id"] == except_category_id:
            continue
        if (
            category["parent_category_id"] == parent_category_id
            and category["category_name"] == category_name
        ):
            return True
    return False


# =====================================
# 장바구니 서비스 함수
# =====================================
def get_or_create_cart(user_id: str) -> dict:
    users = load_users()
    user = find_user_by_user_id(users, user_id)
    if user is None:
        raise ValueError("존재하지 않는 사용자 ID입니다.")

    carts = load_carts(users)
    cart = find_cart_by_user_id(carts, user_id)
    if cart is not None:
        return cart

    cart = {"cart_id": get_next_cart_id(carts), "user_id": normalize_text(user_id)}
    carts.append(cart)
    save_carts(carts)
    return cart


def add_product_to_cart(user_id: str, product_id: str, quantity: str) -> None:
    users = load_users()
    products = load_products()
    if find_user_by_user_id(users, user_id) is None:
        raise ValueError("존재하지 않는 사용자입니다.")

    product = find_product_by_product_id(products, product_id)
    if product is None:
        raise ValueError("존재하지 않는 상품입니다.")
    if int(product["stock"]) == 0:
        raise ValueError("품절 상품은 장바구니에 담을 수 없습니다.")
    if not is_valid_quantity(quantity):
        raise ValueError("수량은 1 이상의 정수여야 합니다.")

    cart = get_or_create_cart(user_id)
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)

    for item in cart_items:
        if item["cart_id"] == cart["cart_id"] and item["product_id"] == normalize_text(product_id):
            item["quantity"] = str(int(item["quantity"]) + int(quantity))
            save_cart_items(cart_items)
            return

    cart_items.append(
        {
            "cart_item_id": get_next_cart_item_id(cart_items, cart["cart_id"]),
            "cart_id": cart["cart_id"],
            "product_id": normalize_text(product_id),
            "quantity": normalize_text(quantity),
        }
    )
    save_cart_items(cart_items)


def remove_product_from_cart(user_id: str, product_id: str) -> None:
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)

    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        raise ValueError("장바구니가 존재하지 않습니다.")

    remaining = []
    removed = False
    for item in cart_items:
        if item["cart_id"] == cart["cart_id"] and item["product_id"] == normalize_text(product_id):
            removed = True
            continue
        remaining.append(item)

    if not removed:
        raise ValueError("장바구니에 존재하지 않는 상품입니다.")
    save_cart_items(remaining)


def get_cart_items_for_user(user_id: str) -> list[dict]:
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)
    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        return []
    return [item for item in cart_items if item["cart_id"] == cart["cart_id"]]


def update_cart_item_quantity(user_id: str, product_id: str, new_quantity: str) -> None:
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)

    if find_user_by_user_id(users, user_id) is None:
        raise ValueError("존재하지 않는 사용자입니다.")
    if not normalize_text(new_quantity).isdigit():
        raise ValueError("숫자만 입력 가능합니다.")
    if int(new_quantity) <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")

    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        raise ValueError("장바구니에 존재하지 않는 상품입니다.")

    for item in cart_items:
        if item["cart_id"] == cart["cart_id"] and item["product_id"] == normalize_text(product_id):
            item["quantity"] = normalize_text(new_quantity)
            save_cart_items(cart_items)
            return

    raise ValueError("장바구니에 존재하지 않는 상품입니다.")


def clear_cart_items_for_user(user_id: str) -> int:
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)
    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        return 0

    removed_count = sum(1 for item in cart_items if item["cart_id"] == cart["cart_id"])
    remaining = [item for item in cart_items if item["cart_id"] != cart["cart_id"]]
    save_cart_items(remaining)
    return removed_count


def build_cart_view_rows(user_id: str) -> list[dict]:
    products = load_products()
    items = get_cart_items_for_user(user_id)
    rows = []
    for item in items:
        product = find_product_by_product_id(products, item["product_id"])
        if product is None:
            continue

        price = int(product["price"])
        quantity = int(item["quantity"])
        stock = int(product["stock"])
        rows.append(
            {
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "price": price,
                "quantity": quantity,
                "item_total": price * quantity,
                "stock": stock,
                "stock_text": "품절" if stock == 0 else f"{stock}개",
                "stock_warning": quantity > stock,
            }
        )
    return sorted(rows, key=lambda row: int(row["product_id"]))


# =====================================
# 쿠폰 / 가상 시간 서비스 함수
# =====================================
def read_current_virtual_time() -> str | None:
    for line in read_lines(VIRTUAL_TIME_FILE):
        value = normalize_text(line)
        if is_valid_virtual_time(value):
            return value
    return None


def prompt_virtual_current_time(prompt_title: str = "가상 현재 시간을 입력하세요.") -> str:
    while True:
        current_virtual_time = read_current_virtual_time()
        print("[가상 현재 시간 입력]")
        if current_virtual_time is not None:
            print(f"현재 가상 일시 : {current_virtual_time}")

        print(f"{prompt_title} (YYMMDDHHMMSS)")
        time_input = input("입력 > ").strip()

        if len(time_input) != 12 or not time_input.isdigit():
            print("오류 : 올바른 시간 형식으로 입력하세요.")
            continue
        if not is_valid_virtual_time(time_input):
            print("오류 : 존재하지 않는 날짜 또는 시간입니다.")
            continue
        if current_virtual_time is not None and time_input < current_virtual_time:
            print("오류 : 이전 시간으로 이동할 수 없습니다.")
            continue

        write_lines(VIRTUAL_TIME_FILE, [time_input])
        return time_input


def calculate_expires_at(issued_at: str, valid_days: str | int) -> str:
    if not is_valid_virtual_time(issued_at):
        raise ValueError("발급 시간이 올바르지 않습니다.")
    if not str(valid_days).isdigit() or int(valid_days) <= 0:
        raise ValueError("유효 기간은 1 이상의 정수여야 합니다.")

    issued_dt = datetime.strptime(issued_at, "%y%m%d%H%M%S")
    return (issued_dt + timedelta(days=int(valid_days))).strftime("%y%m%d%H%M%S")


def issue_coupon_to_user(user_id: str, coupon_id: str, issued_at: str) -> dict:
    users = load_users()
    coupons = load_coupons()
    user_coupons = load_user_coupons(users, coupons)

    if find_user_by_user_id(users, user_id) is None:
        raise ValueError("존재하지 않는 사용자입니다.")
    coupon = find_coupon_by_coupon_id(coupons, coupon_id)
    if coupon is None:
        raise ValueError("존재하지 않는 쿠폰입니다.")
    if not is_valid_virtual_time(issued_at):
        raise ValueError("발급 시간이 올바르지 않습니다.")

    user_coupon = {
        "user_coupon_id": get_next_user_coupon_id(user_coupons),
        "user_id": normalize_text(user_id),
        "coupon_id": normalize_text(coupon_id),
        "issued_at": normalize_text(issued_at),
        "expires_at": calculate_expires_at(issued_at, coupon["valid_days"]),
        "used_status": "UNUSED",
    }
    user_coupons.append(user_coupon)
    save_user_coupons(user_coupons)
    return user_coupon


def issue_signup_coupon_if_needed(user_id: str) -> None:
    signup_coupons = [
        coupon for coupon in load_coupons() if coupon["issue_type"] == "SIGNUP"
    ]
    if not signup_coupons:
        return

    try:
        issued_at = prompt_virtual_current_time("신규 회원 쿠폰 발급 기준 시간을 입력하세요.")
        issue_coupon_to_user(user_id, signup_coupons[0]["coupon_id"], issued_at)
        print("신규 회원 쿠폰 1장이 발급되었습니다.")
    except ValueError as error:
        print(f"오류 : {error}")
    except Exception:
        print("오류 : 쿠폰을 발급하지 못했습니다.")


def issue_order_count_coupon_if_needed(user_id: str, order_time: str) -> list[dict]:
    if not is_valid_virtual_time(order_time):
        return []

    orders = load_orders()
    coupons = load_coupons()
    user_order_count = sum(
        1
        for order in orders
        if order["user_id"] == normalize_text(user_id)
        and order["order_status"] in {"PENDING", "ACCEPTED", "CANCEL_REQUESTED"}
    )
    issued = []

    for coupon in coupons:
        if coupon["issue_type"] != "ORDER_COUNT":
            continue
        threshold = int(coupon["issue_threshold"])
        if threshold <= 0:
            continue
        if user_order_count > 0 and user_order_count % threshold == 0:
            try:
                issued.append(issue_coupon_to_user(user_id, coupon["coupon_id"], order_time))
            except ValueError:
                continue

    return issued


def calculate_coupon_target_amount(
    coupon: dict,
    order_rows: list[dict],
    categories: list[dict],
    product_categories: list[dict],
) -> int:
    target_type = coupon["target_type"]
    target_id = coupon["target_id"]

    if target_type == "ALL":
        return sum(int(row["item_total"]) for row in order_rows)

    if target_type == "PRODUCT":
        return sum(
            int(row["item_total"])
            for row in order_rows
            if row["product_id"] == target_id
        )

    if target_type == "CATEGORY":
        target_category_ids = get_category_descendant_ids(target_id, categories)
        matched_product_ids = {
            item["product_id"]
            for item in product_categories
            if item["category_id"] in target_category_ids
        }
        return sum(
            int(row["item_total"])
            for row in order_rows
            if row["product_id"] in matched_product_ids
        )

    return 0


def calculate_coupon_discount(
    coupon: dict,
    order_rows: list[dict],
    categories: list[dict],
    product_categories: list[dict],
) -> int:
    target_amount = calculate_coupon_target_amount(
        coupon,
        order_rows,
        categories,
        product_categories,
    )
    if target_amount <= 0:
        return 0

    if coupon["discount_type"] == "FIXED":
        discount = int(coupon["discount_value"])
    elif coupon["discount_type"] == "RATE":
        discount = target_amount * int(coupon["discount_value"]) // 100
    else:
        return 0

    original_price = sum(int(row["item_total"]) for row in order_rows)
    return max(0, min(discount, target_amount, original_price))


def get_available_user_coupons(
    user_id: str,
    order_rows: list[dict],
    original_price: int,
    current_time: str,
) -> list[dict]:
    users = load_users()
    coupons = load_coupons()
    user_coupons = load_user_coupons(users, coupons)
    categories = load_categories()
    products = load_products()
    product_categories = load_product_categories(products, categories)
    coupon_map = {coupon["coupon_id"]: coupon for coupon in coupons}
    available = []

    for user_coupon in user_coupons:
        if user_coupon["user_id"] != normalize_text(user_id):
            continue
        if user_coupon["used_status"] != "UNUSED":
            continue
        if not (user_coupon["issued_at"] <= current_time <= user_coupon["expires_at"]):
            continue

        coupon = coupon_map.get(user_coupon["coupon_id"])
        if coupon is None:
            continue
        if original_price < int(coupon["min_order_price"]):
            continue
        discount = calculate_coupon_discount(
            coupon,
            order_rows,
            categories,
            product_categories,
        )
        if discount <= 0:
            continue

        available.append(
            {
                **user_coupon,
                "coupon": coupon,
                "discount_price": discount,
            }
        )

    return sorted(
        available,
        key=lambda item: (int(item["coupon_id"]), item["expires_at"], int(item["user_coupon_id"])),
    )


def describe_coupon_discount(coupon: dict) -> str:
    if coupon["discount_type"] == "FIXED":
        return f"{int(coupon['discount_value']):,}원 할인"
    if coupon["discount_type"] == "RATE":
        return f"{coupon['discount_value']}% 할인"
    return "할인"


# =====================================
# 주문 서비스 함수
# =====================================
def get_current_order_time() -> str:
    current_virtual_time = read_current_virtual_time()
    if current_virtual_time is not None:
        return current_virtual_time
    return datetime.now().strftime("%y%m%d%H%M%S")


def rows_for_selected_products(rows: list[dict], selected_product_ids: list[str] | None) -> list[dict]:
    if selected_product_ids is None:
        return rows
    selected_set = {normalize_text(product_id) for product_id in selected_product_ids}
    return [row for row in rows if row["product_id"] in selected_set]


def create_order_from_cart(
    user_id: str,
    selected_product_ids: list[str] | None = None,
    order_time: str | None = None,
    selected_user_coupon_id: str = "0",
) -> dict:
    if order_time is None:
        order_time = get_current_order_time()
    if not is_valid_virtual_time(order_time):
        raise ValueError("주문 시간이 올바르지 않습니다.")

    users = load_users()
    products = load_products()
    categories = load_categories()
    product_categories = load_product_categories(products, categories)
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)
    orders = load_orders()
    order_items = load_order_items()
    coupons = load_coupons()
    user_coupons = load_user_coupons(users, coupons)

    if find_user_by_user_id(users, user_id) is None:
        raise ValueError("존재하지 않는 사용자입니다.")

    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        raise ValueError("장바구니가 비어 있습니다.")

    user_cart_items = [
        item for item in cart_items if item["cart_id"] == cart["cart_id"]
    ]
    if not user_cart_items:
        raise ValueError("장바구니가 비어 있습니다.")

    selected_set = None
    if selected_product_ids is not None:
        selected_set = {normalize_text(product_id) for product_id in selected_product_ids}
        if not selected_set:
            raise ValueError("주문할 상품을 선택해야 합니다.")

    target_items = [
        item
        for item in user_cart_items
        if selected_set is None or item["product_id"] in selected_set
    ]
    if not target_items:
        raise ValueError("주문할 상품을 선택해야 합니다.")

    order_rows = []
    for item in target_items:
        product = find_product_by_product_id(products, item["product_id"])
        if product is None:
            raise ValueError("유효하지 않은 상품이 장바구니에 있습니다.")
        if int(item["quantity"]) > int(product["stock"]):
            raise ValueError("재고가 부족한 상품이 포함되어 있습니다.")
        price = int(product["price"])
        quantity = int(item["quantity"])
        order_rows.append(
            {
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "price": price,
                "quantity": quantity,
                "item_total": price * quantity,
            }
        )

    original_price = sum(row["item_total"] for row in order_rows)
    if original_price > 1_000_000:
        raise ValueError("총 주문 금액은 1,000,000원을 초과할 수 없습니다.")

    selected_user_coupon_id = normalize_text(selected_user_coupon_id)
    discount_price = 0
    if selected_user_coupon_id != "0":
        user_coupon = find_user_coupon_by_id(user_coupons, selected_user_coupon_id)
        if user_coupon is None or user_coupon["user_id"] != normalize_text(user_id):
            raise ValueError("사용할 수 없는 쿠폰입니다.")
        if user_coupon["used_status"] != "UNUSED":
            raise ValueError("이미 사용된 쿠폰입니다.")
        if not (user_coupon["issued_at"] <= order_time <= user_coupon["expires_at"]):
            raise ValueError("사용할 수 없는 쿠폰입니다.")

        coupon = find_coupon_by_coupon_id(coupons, user_coupon["coupon_id"])
        if coupon is None:
            raise ValueError("사용할 수 없는 쿠폰입니다.")
        if original_price < int(coupon["min_order_price"]):
            raise ValueError("쿠폰 최소 주문 금액을 만족하지 않습니다.")

        discount_price = calculate_coupon_discount(
            coupon,
            order_rows,
            categories,
            product_categories,
        )
        if discount_price <= 0:
            raise ValueError("사용할 수 없는 쿠폰입니다.")

        user_coupon["used_status"] = "USED"

    total_price = original_price - discount_price
    new_order = {
        "order_id": get_next_order_id(orders),
        "user_id": normalize_text(user_id),
        "original_price": str(original_price),
        "discount_price": str(discount_price),
        "total_price": str(total_price),
        "order_status": "PENDING",
        "order_time": normalize_text(order_time),
        "user_coupon_id": selected_user_coupon_id,
    }
    orders.append(new_order)

    next_order_item_id = get_next_order_item_id(order_items)
    for row in order_rows:
        order_items.append(
            {
                "order_item_id": next_order_item_id,
                "order_id": new_order["order_id"],
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "price": str(row["price"]),
                "quantity": str(row["quantity"]),
            }
        )
        next_order_item_id = str(int(next_order_item_id) + 1)

    if selected_set is None:
        remaining_cart_items = [
            item for item in cart_items if item["cart_id"] != cart["cart_id"]
        ]
    else:
        remaining_cart_items = [
            item
            for item in cart_items
            if not (item["cart_id"] == cart["cart_id"] and item["product_id"] in selected_set)
        ]

    save_orders(orders)
    save_order_items(order_items)
    save_cart_items(remaining_cart_items)
    save_user_coupons(user_coupons)
    issue_order_count_coupon_if_needed(user_id, order_time)

    return new_order


def request_order_cancellation(user_id: str, order_id: str) -> dict:
    orders = load_orders()
    order = find_order_by_order_id(orders, order_id)
    if order is None:
        raise ValueError("존재하지 않는 주문 ID입니다.")
    if order["user_id"] != normalize_text(user_id):
        raise ValueError("본인의 주문만 취소 요청할 수 있습니다.")
    if order["order_status"] != "PENDING":
        raise ValueError("취소할 수 없는 상태입니다.")

    order["order_status"] = "CANCEL_REQUESTED"
    save_orders(orders)
    return order


def is_order_stock_insufficient(order_id: str) -> bool:
    products = load_products()
    order_items = load_order_items()
    for item in get_order_items_by_order_id(order_items, order_id):
        product = find_product_by_product_id(products, item["product_id"])
        if product is None:
            return True
        if int(item["quantity"]) > int(product["stock"]):
            return True
    return False


def update_order_status_by_admin(order_id: str, action: str) -> dict:
    orders = load_orders()
    order_items = load_order_items()
    products = load_products()
    order = find_order_by_order_id(orders, order_id)
    if order is None:
        raise ValueError("등록되지 않은 주문 ID입니다.")

    action = normalize_text(action).lower()
    if action == "approve":
        if order["order_status"] != "PENDING":
            raise ValueError("처리가 완료된 주문입니다.")
        if is_order_stock_insufficient(order_id):
            raise ValueError("수량 부족으로 수락 불가능한 주문입니다.")

        for item in get_order_items_by_order_id(order_items, order_id):
            product = find_product_by_product_id(products, item["product_id"])
            product["stock"] = str(int(product["stock"]) - int(item["quantity"]))

        order["order_status"] = "ACCEPTED"
        save_products(products)
        save_orders(orders)
        return order

    if action == "reject":
        if order["order_status"] != "PENDING":
            raise ValueError("처리가 완료된 주문입니다.")
        if not is_order_stock_insufficient(order_id):
            raise ValueError("거절 가능한 주문이 아닙니다.")

        order["order_status"] = "REJECTED"
        save_orders(orders)
        return order

    if action == "cancel":
        if order["order_status"] != "CANCEL_REQUESTED":
            raise ValueError("취소 가능한 주문이 아닙니다.")

        order["order_status"] = "CANCELLED"
        save_orders(orders)
        return order

    raise ValueError("지원하지 않는 관리자 주문 처리 동작입니다.")


# =====================================
# 상품 조회 / 검색 프롬프트
# =====================================
def print_product_table(
    products: list[dict],
    category_name_map: dict[str, str],
    product_categories: list[dict],
) -> None:
    categories = load_categories()
    rows = []
    for product in products:
        rows.append(
            [
                product["product_id"],
                product["product_name"],
                get_product_category_names(product["product_id"], product_categories, categories),
                f"{int(product['price']):,}원",
                f"{product['stock']}개",
            ]
        )

    headers = ["상품 ID", "상품명", "카테고리", "가격", "재고"]
    widths = [
        max(get_display_width(row[index]) for row in rows + [headers])
        for index in range(len(headers))
    ]
    print(" | ".join(pad_display_text(headers[index], widths[index]) for index in range(len(headers))))
    print("-+-".join("-" * widths[index] for index in range(len(headers))))
    for row in rows:
        print(" | ".join(pad_display_text(row[index], widths[index]) for index in range(len(row))))


def sort_products_by_product_id(products: list[dict]) -> list[dict]:
    return sorted(products, key=lambda product: int(product["product_id"]))


def print_category_tree(categories: list[dict]) -> None:
    children_by_parent: dict[str, list[dict]] = defaultdict(list)
    for category in categories:
        children_by_parent[category["parent_category_id"]].append(category)

    def print_children(parent_id: str, depth: int) -> None:
        for category in sorted(children_by_parent.get(parent_id, []), key=lambda item: int(item["category_id"])):
            indent = "  " * depth
            print(f"{indent}{category['category_id']}. {category['category_name']}")
            print_children(category["category_id"], depth + 1)

    print("** 카테고리 **")
    print_children("0", 0)


def show_all_products_prompt() -> None:
    print("[전체 상품 조회]")
    products = sort_products_by_product_id(load_products())
    if not products:
        print("오류 : 등록된 상품이 없습니다.")
        return

    categories = load_categories()
    product_categories = load_product_categories(products, categories)
    print_product_table(products, build_category_name_map(categories), product_categories)


def show_products_by_category_prompt() -> None:
    products = sort_products_by_product_id(load_products())
    if not products:
        print("등록된 상품이 없습니다.")
        return

    categories = load_categories()
    product_categories = load_product_categories(products, categories)
    category_name_map = build_category_name_map(categories)

    while True:
        print("[카테고리별 조회]")
        print_category_tree(categories)
        category_input = input("카테고리 ID 입력 (0 : 뒤로가기)> ").strip()
        if category_input == "0":
            return
        if not is_valid_numeric_id(category_input) or category_input not in category_name_map:
            print("오류: 존재하는 카테고리 ID를 입력하세요.")
            continue

        target_category_ids = get_category_descendant_ids(category_input, categories)
        matched_product_ids = {
            item["product_id"]
            for item in product_categories
            if item["category_id"] in target_category_ids
        }
        filtered_products = [
            product for product in products if product["product_id"] in matched_product_ids
        ]
        if not filtered_products:
            print("해당 카테고리에 등록된 상품이 없습니다.")
            return

        print_product_table(filtered_products, category_name_map, product_categories)
        return


def normalize_search_key(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def show_products_by_name_prompt() -> None:
    categories = load_categories()
    product_categories = load_product_categories(load_products(), categories)
    products = sort_products_by_product_id(load_products())

    print("[상품명 검색]")
    while True:
        keyword = input("검색어 입력 > ").strip()
        if keyword == "":
            print("오류: 검색어를 1자 이상 입력하세요.")
            continue

        normalized_keyword = normalize_search_key(keyword)
        filtered_products = [
            product
            for product in products
            if normalized_keyword in normalize_search_key(product["product_name"])
        ]
        if not filtered_products:
            print("검색 결과가 없습니다.")
            print(f"입력한 검색어: {keyword}")
            return

        print_product_table(filtered_products, build_category_name_map(categories), product_categories)
        return


def product_search_main_prompt() -> None:
    while True:
        print("[상품 조회 / 검색]")
        print("1. 전체 상품 조회")
        print("2. 카테고리별 조회")
        print("3. 상품명 검색")
        print("0. 이전 메뉴")
        choice = input("선택 > ").strip()

        if choice == "1":
            show_all_products_prompt()
        elif choice == "2":
            show_products_by_category_prompt()
        elif choice == "3":
            show_products_by_name_prompt()
        elif choice == "0":
            return
        else:
            print("오류: 올바른 메뉴 번호를 입력하세요.")


# =====================================
# 장바구니 프롬프트
# =====================================
def print_cart_view(user_id: str) -> None:
    try:
        rows = build_cart_view_rows(user_id)
    except Exception:
        print("오류: 장바구니 정보를 불러오지 못했습니다.")
        return

    print("[장바구니 조회]")
    if not rows:
        print("장바구니가 비어 있습니다.")
        return

    print(f"총 상품 종류: {len(rows)}개")
    print(f"총 금액: {format_money(sum(row['item_total'] for row in rows))}")
    print("------------------------------")
    for index, row in enumerate(rows, start=1):
        print(f"[{index}]")
        print(f"상품 ID: {row['product_id']}")
        print(f"상품명: {row['product_name']}")
        print(f"가격: {format_money(row['price'])}")
        print(f"수량: {row['quantity']}개")
        print(f"상품 합계: {format_money(row['item_total'])}")
        print(f"재고: {row['stock_text']}")
        if row["stock_warning"]:
            print("재고 경고: 현재 재고보다 많이 담겨 있습니다.")
        print("------------------------------")


def prompt_add_product_to_cart(current_user: dict) -> None:
    while True:
        print("[상품 추가]")
        product_id = input("상품 ID 입력 > ").strip()
        quantity = input("수량 입력 > ").strip()

        if not is_valid_numeric_id(product_id):
            print("오류: 존재하지 않는 상품입니다.")
            continue
        if not is_valid_quantity(quantity):
            print("오류: 수량은 1 이상 입력하세요.")
            continue

        try:
            add_product_to_cart(current_user["user_id"], product_id, quantity)
            print("상품이 장바구니에 추가되었습니다.")
            return
        except ValueError as error:
            print(f"오류: {error}")
        except Exception:
            print("오류: 장바구니를 저장하지 못했습니다.")
            return


def prompt_remove_product_from_cart(current_user: dict) -> None:
    while True:
        print("[상품 삭제]")
        product_id = input("삭제할 상품 ID 입력 > ").strip()
        if not is_valid_numeric_id(product_id):
            print("오류: 장바구니에 존재하지 않는 상품입니다.")
            continue

        try:
            remove_product_from_cart(current_user["user_id"], product_id)
            print("상품이 장바구니에서 삭제되었습니다.")
            return
        except ValueError as error:
            print(f"오류: {error}")
        except Exception:
            print("오류: 장바구니를 저장하지 못했습니다.")
            return


def prompt_update_cart_quantity(current_user: dict) -> None:
    user_id = current_user["user_id"]
    if not get_cart_items_for_user(user_id):
        print("장바구니가 비어 있습니다.")
        return

    while True:
        print("[수량 변경]")
        product_id = input("변경할 상품 ID 입력(0: 이전 메뉴) > ").strip()
        if product_id == "0":
            return
        if not is_valid_numeric_id(product_id):
            print("오류 : 숫자만 입력 가능합니다.")
            continue

        new_quantity = input("변경할 수량 입력 > ").strip()
        try:
            update_cart_item_quantity(user_id, product_id, new_quantity)
            print("장바구니 수량이 변경되었습니다.")
            return
        except ValueError as error:
            print(f"오류 : {error}")
        except Exception:
            print("오류 : 장바구니를 저장하지 못했습니다.")
            return


def prompt_clear_cart(current_user: dict) -> None:
    user_id = current_user["user_id"]
    if not get_cart_items_for_user(user_id):
        print("장바구니가 비어 있습니다.")
        return

    while True:
        print("[장바구니 전체 비우기]")
        confirm = input("정말 장바구니를 모두 비우시겠습니까? (Yes/No) > ").strip()
        if confirm == "No":
            print("장바구니 전체 비우기를 취소했습니다.")
            return
        if confirm != "Yes":
            print("오류: Yes 또는 No 를 입력하세요.")
            continue

        try:
            clear_cart_items_for_user(user_id)
            print("장바구니를 모두 비웠습니다.")
        except Exception:
            print("오류: 장바구니를 저장하지 못했습니다.")
        return


def cart_main_prompt(current_user: dict) -> None:
    try:
        get_or_create_cart(current_user["user_id"])
    except Exception:
        print("오류: 장바구니 정보를 불러오지 못했습니다.")
        return

    while True:
        print("[장바구니 메뉴]")
        print("1. 장바구니 조회")
        print("2. 상품 추가")
        print("3. 상품 삭제")
        print("4. 수량 변경")
        print("5. 장바구니 전체 비우기")
        print("0. 이전 메뉴")
        choice = input("선택 > ").strip()

        if choice == "1":
            print_cart_view(current_user["user_id"])
        elif choice == "2":
            prompt_add_product_to_cart(current_user)
        elif choice == "3":
            prompt_remove_product_from_cart(current_user)
        elif choice == "4":
            prompt_update_cart_quantity(current_user)
        elif choice == "5":
            prompt_clear_cart(current_user)
        elif choice == "0":
            return
        else:
            if choice.isdigit():
                print("오류 : 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류 : 숫자만 입력 가능합니다.")


# =====================================
# 주문 프롬프트
# =====================================
def prompt_select_partial_order_items(current_user: dict, rows: list[dict]) -> list[str] | None:
    while True:
        print("[부분 주문 상품 선택]")
        print("현재 장바구니 내역입니다:")
        for index, row in enumerate(rows, start=1):
            print(
                f"{index}. 상품 ID: {row['product_id']} / 상품명: {row['product_name']} / "
                f"수량: {row['quantity']}개 / 상품 합계: {format_money(row['item_total'])}"
            )
        raw_input = input("주문할 상품 ID 입력(여러 개 선택 시 쉼표로 구분, 0: 취소) > ").strip()
        if raw_input == "0":
            return None
        if raw_input == "":
            print("오류: 주문할 상품을 선택해야 합니다.")
            continue
        if not re.fullmatch(r"[0-9,\s]+", raw_input):
            print("오류: 올바른 상품 ID 를 입력하세요.")
            continue

        product_ids = []
        seen = set()
        for token in [token.strip() for token in raw_input.split(",")]:
            if token == "":
                continue
            if not is_valid_numeric_id(token):
                print("오류: 올바른 상품 ID 를 입력하세요.")
                break
            if token not in seen:
                seen.add(token)
                product_ids.append(token)
        else:
            if not product_ids:
                print("오류: 주문할 상품을 선택해야 합니다.")
                continue
            row_product_ids = {row["product_id"] for row in rows}
            if any(product_id not in row_product_ids for product_id in product_ids):
                print("오류: 장바구니에 존재하지 않는 상품입니다.")
                continue
            return product_ids


def prompt_use_coupon(
    current_user: dict,
    order_rows: list[dict],
    original_price: int,
    current_time: str,
) -> tuple[str, int, str]:
    available = get_available_user_coupons(
        current_user["user_id"],
        order_rows,
        original_price,
        current_time,
    )
    if not available:
        print("현재 주문에 사용할 수 있는 쿠폰이 없습니다.")
        return "0", 0, "없음"

    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in available:
        grouped[item["coupon_id"]].append(item)

    display_items = []
    for coupon_id in sorted(grouped, key=int):
        items = sorted(grouped[coupon_id], key=lambda item: (item["expires_at"], int(item["user_coupon_id"])))
        display_items.append((items[0]["coupon"], items))

    while True:
        print("[사용 가능 쿠폰 목록]")
        print(f"총 {len(available)}장")
        for index, (coupon, items) in enumerate(display_items, start=1):
            print(
                f"{index}. {coupon['coupon_name']} - {describe_coupon_discount(coupon)} "
                f"({len(items)}장)"
            )
        print("0. 쿠폰 사용 안 함")
        choice = input("선택 > ").strip()

        if choice == "0":
            return "0", 0, "없음"
        if not choice.isdigit() or not (1 <= int(choice) <= len(display_items)):
            print("오류: 사용할 수 없는 쿠폰 번호입니다.")
            continue

        coupon, items = display_items[int(choice) - 1]
        selected = sorted(items, key=lambda item: (item["expires_at"], int(item["user_coupon_id"])))[0]
        discount_price = calculate_coupon_discount(
            coupon,
            order_rows,
            load_categories(),
            load_product_categories(load_products(), load_categories()),
        )
        print(f"{coupon['coupon_name']}이 적용되었습니다.")
        return selected["user_coupon_id"], discount_price, coupon["coupon_name"]


def prompt_order_confirm(current_user: dict) -> None:
    print("[주문 확정]")
    try:
        order_time = prompt_virtual_current_time("가상 현재 시간을 입력하세요.")
        rows = build_cart_view_rows(current_user["user_id"])
    except Exception:
        print("오류: 장바구니 정보를 불러오지 못했습니다.")
        return

    if not rows:
        print("오류: 장바구니가 비어 있습니다.")
        return

    print("현재 장바구니 내역입니다:")
    for row in rows:
        print(f"- {row['product_name']} ({row['quantity']}개): {format_money(row['item_total'])}")
    print("---------------------------------------")
    print("주문 방식을 선택하세요.")
    print("1. 전체 주문")
    print("2. 부분 주문")
    print("0. 뒤로가기")
    choice = input("선택 > ").strip()

    if choice == "0":
        return
    if choice == "1":
        selected_product_ids = None
        order_rows = rows
    elif choice == "2":
        selected_product_ids = prompt_select_partial_order_items(current_user, rows)
        if selected_product_ids is None:
            return
        order_rows = rows_for_selected_products(rows, selected_product_ids)
    else:
        print("오류 : 올바른 메뉴 번호를 입력하세요.")
        return

    original_price = sum(int(row["item_total"]) for row in order_rows)
    if original_price > 1_000_000:
        print("오류: 총 주문 금액은 1,000,000원을 초과할 수 없습니다.")
        return
    if any(row["stock_warning"] for row in order_rows):
        print("오류: 재고가 부족한 상품이 포함되어 있습니다.")
        return

    print(f"쿠폰 적용 전 금액 : {format_money(original_price)}")
    selected_user_coupon_id, discount_price, coupon_name = prompt_use_coupon(
        current_user,
        order_rows,
        original_price,
        order_time,
    )
    print(f"쿠폰 할인 금액 : {format_money(discount_price)}")
    print(f"최종 결제 금액 : {format_money(original_price - discount_price)}")

    confirm = input("정말 주문하시겠습니까? (Yes/No) 입력 > ").strip()
    if confirm != "Yes":
        print("주문이 취소되었습니다.")
        return

    try:
        order = create_order_from_cart(
            current_user["user_id"],
            selected_product_ids,
            order_time,
            selected_user_coupon_id,
        )
        print("주문이 완료되었습니다.")
        print(f"주문 번호 : {order['order_id']}")
        print(f"주문 시간 : {order['order_time']}")
        print(f"주문 상태 : {order['order_status']}")
        if selected_product_ids is None:
            print("장바구니를 비웠습니다.")
        else:
            print("주문에 포함된 상품만 장바구니에서 삭제됩니다.")
    except ValueError as error:
        print(f"오류: {error}")
    except Exception:
        print("오류: 주문을 처리하지 못했습니다.")


def resolve_coupon_name(order: dict) -> str:
    if order.get("user_coupon_id", "0") == "0":
        return "없음"
    coupons = load_coupons()
    user_coupons = load_user_coupons(load_users(), coupons)
    user_coupon = find_user_coupon_by_id(user_coupons, order["user_coupon_id"])
    if user_coupon is None:
        return "알 수 없음"
    coupon = find_coupon_by_coupon_id(coupons, user_coupon["coupon_id"])
    if coupon is None:
        return "알 수 없음"
    return coupon["coupon_name"]


def prompt_order_history(current_user: dict) -> None:
    user_id = normalize_text(current_user["user_id"])
    while True:
        orders = [order for order in load_orders() if order["user_id"] == user_id]
        orders.sort(key=lambda order: order["order_time"], reverse=True)

        print(f"[나의 주문 내역] 총 {len(orders)}건")
        if not orders:
            print("오류: 조회할 주문 내역이 없습니다.")
            return

        for index, order in enumerate(orders, start=1):
            try:
                order_time_text = datetime.strptime(order["order_time"], "%y%m%d%H%M%S").strftime("%y/%m/%d %H:%M:%S")
            except ValueError:
                order_time_text = order["order_time"]
            print(f"[{index}] 주문 ID: {order['order_id']}")
            print(f"주문일시 : {order_time_text}")
            print(f"총 금액 : {format_money(int(order['original_price']))}")
            print(f"쿠폰 할인 금액 : {format_money(int(order['discount_price']))}")
            print(f"최종 결제 금액 : {format_money(int(order['total_price']))}")
            print(f"사용 쿠폰 : {resolve_coupon_name(order)}")
            print(f"상태 : {order['order_status']}")
            print()

        choice = input("상세 조회할 주문 ID 입력 (0: 이전 메뉴) > ").strip()
        if choice == "0":
            return
        selected_order = find_order_by_order_id(orders, choice)
        if selected_order is None:
            print("오류 : 올바른 주문 ID를 입력하세요.")
            continue
        prompt_order_detail(selected_order)


def prompt_order_detail(order: dict) -> None:
    try:
        order_items = load_order_items()
        products = load_products()
    except Exception:
        print("오류: 주문 상세 내역을 불러오지 못했습니다.")
        return

    items = get_order_items_by_order_id(order_items, order["order_id"])
    print("[주문 상세 내역]")
    print(f"- 주문 ID: {order['order_id']}")
    print(f"- 주문상태 : {order['order_status']}")
    print()

    for index, item in enumerate(items, start=1):
        print(
            f"{index}. {item['product_name']} ({item['quantity']}개) : "
            f"{format_money(int(item['price']))}"
        )
        product = find_product_by_product_id(products, item["product_id"])
        if product is None:
            print("INFO: 현재 상품 정보가 삭제되었습니다.")
        elif product["product_name"] != item["product_name"] or product["price"] != item["price"]:
            print("INFO: 주문 당시 상품명 또는 가격이 현재 상품 정보와 다릅니다.")

    print()
    print(f"- 쿠폰 적용 전 금액 : {format_money(int(order['original_price']))}")
    print(f"- 쿠폰 할인 금액 : {format_money(int(order['discount_price']))}")
    print(f"- 사용 쿠폰 : {resolve_coupon_name(order)}")
    print(f"- 총 결제 금액 : {format_money(int(order['total_price']))}")
    print("(엔터를 누르면 주문 목록으로 돌아갑니다.)")

    while True:
        if input().strip() == "":
            return
        print("오류 : 엔터를 입력하세요.")


def prompt_order_cancel_request(current_user: dict) -> None:
    user_id = normalize_text(current_user["user_id"])
    while True:
        print("[주문 취소 요청]")
        order_id = input("취소할 주문 ID를 입력하세요 > ").strip()
        order = find_order_by_order_id(load_orders(), order_id)
        if order is None:
            print("오류 : 존재하지 않는 주문 ID입니다.")
            continue
        if order["user_id"] != user_id:
            print("오류 : 본인의 주문만 취소 요청할 수 있습니다.")
            continue
        if order["order_status"] != "PENDING":
            print("오류 : 취소할 수 없는 상태입니다.")
            continue

        confirm = input("정말 취소 요청을 보내시겠습니까? (실행: ABORT / 취소: 기타 입력) > ").strip()
        if confirm != "ABORT":
            print("취소 요청을 취소했습니다.")
            return

        try:
            request_order_cancellation(user_id, order_id)
            print("취소 요청이 정상적으로 접수되었습니다. (상태: CANCEL_REQUESTED)")
            return
        except ValueError as error:
            print(f"오류 : {error}")


def prompt_my_coupons(current_user: dict) -> None:
    try:
        current_time = prompt_virtual_current_time("쿠폰 조회 기준 시간을 입력하세요.")
        coupons = load_coupons()
        user_coupons = [
            item
            for item in load_user_coupons(load_users(), coupons)
            if item["user_id"] == current_user["user_id"]
        ]
    except Exception:
        print("오류 : 쿠폰 정보를 불러오지 못했습니다.")
        return

    if not user_coupons:
        print("보유한 쿠폰이 없습니다.")
        return

    coupon_map = {coupon["coupon_id"]: coupon for coupon in coupons}
    summary = {}
    for user_coupon in user_coupons:
        coupon = coupon_map.get(user_coupon["coupon_id"])
        if coupon is None:
            continue
        coupon_id = coupon["coupon_id"]
        if coupon_id not in summary:
            summary[coupon_id] = {
                "coupon": coupon,
                "total": 0,
                "available": 0,
                "used": 0,
                "expired": 0,
            }
        summary[coupon_id]["total"] += 1
        if user_coupon["used_status"] == "USED":
            summary[coupon_id]["used"] += 1
        elif current_time > user_coupon["expires_at"]:
            summary[coupon_id]["expired"] += 1
        elif user_coupon["issued_at"] <= current_time <= user_coupon["expires_at"]:
            summary[coupon_id]["available"] += 1

    print("[내 쿠폰 목록]")
    print(f"총 {len(user_coupons)}장")
    for index, coupon_id in enumerate(sorted(summary, key=int), start=1):
        item = summary[coupon_id]
        coupon = item["coupon"]
        print(
            f"{index}. {coupon['coupon_name']} - {describe_coupon_discount(coupon)} "
            f"({item['total']}장)"
        )
        print(
            f"전체 {item['total']}장 / 사용 가능 {item['available']}장 / "
            f"사용 완료 {item['used']}장 / 만료 {item['expired']}장"
        )

    while True:
        print("0. 이전 메뉴")
        choice = input("선택 > ").strip()
        if choice == "0":
            return
        print("오류: 올바른 메뉴 번호를 입력하세요.")


def order_main_prompt(current_user: dict) -> None:
    while True:
        print("[주문 관리]")
        print("1. 주문하기 (장바구니 내역)")
        print("2. 주문 내역 조회")
        print("3. 주문 취소 요청")
        print("4. 내 쿠폰 조회")
        print("0. 이전 메뉴")
        choice = input("선택 > ").strip()

        if choice == "1":
            prompt_order_confirm(current_user)
        elif choice == "2":
            prompt_order_history(current_user)
        elif choice == "3":
            prompt_order_cancel_request(current_user)
        elif choice == "4":
            prompt_my_coupons(current_user)
        elif choice == "0":
            return
        else:
            print("오류 : 올바른 메뉴 번호를 입력하세요.")


# =====================================
# 관리자 프롬프트
# =====================================
def admin_add_product_flow() -> bool:
    products = load_products()
    categories = load_categories()

    while True:
        product_name = input("판매할 상품의 이름을 등록하세요 (이전 : [Enter] 입력) : ").strip()
        if product_name == "":
            return False
        if not is_valid_product_name(product_name):
            print("오류 : 상품명 형식이 올바르지 않습니다.")
            continue
        if find_product_by_name(products, product_name) is not None:
            print("오류 : 판매중인 상품명과 동일합니다.")
            continue
        break

    while True:
        print("[카테고리 등록]")
        print("판매할 상품의 카테고리를 등록하세요. 여러 개 입력 시 쉼표(,)로 구분하세요.")
        print_category_tree(categories)
        category_input = input("카테고리 ID 입력 > ").strip()
        try:
            category_ids = parse_category_id_list(category_input, categories)
            break
        except ValueError as error:
            print(error)

    while True:
        price = input("판매할 상품의 가격을 등록하세요 : ").strip()
        if not is_valid_price(price):
            print("오류 : 가격은 1~1,000,000 사이의 숫자여야 합니다.")
            continue
        break

    while True:
        stock = input("판매할 상품의 재고를 등록하세요 : ").strip()
        if not is_valid_stock(stock):
            print("오류 : 재고는 0 이상의 숫자여야 합니다.")
            continue
        break

    try:
        create_product(category_ids, product_name, price, stock)
        print("상품이 등록되었습니다.")
        return True
    except ValueError as error:
        print(f"오류 : {error}")
        return False


def admin_product_edit_flow() -> bool:
    products = load_products()
    if not products:
        print("등록된 상품이 없습니다.")
        return False

    while True:
        product_id = input("수정할 상품 ID를 입력하세요 (0: 이전 메뉴) > ").strip()
        if product_id == "0":
            return False
        product = find_product_by_product_id(products, product_id)
        if product is None:
            print("오류 : 등록되지 않은 상품 ID입니다.")
            continue
        break

    while True:
        print("[상품 수정]")
        print("1. 상품명 수정")
        print("2. 카테고리 수정")
        print("3. 가격 수정")
        print("4. 재고 수정")
        print("0. 뒤로가기")
        choice = input("선택 > ").strip()
        try:
            if choice == "0":
                return False
            if choice == "1":
                value = input("새 상품명을 입력하세요 > ").strip()
                update_product(product_id, new_product_name=value)
            elif choice == "2":
                categories = load_categories()
                print_category_tree(categories)
                value = input("새 카테고리 ID 입력(여러 개는 쉼표로 구분) > ").strip()
                category_ids = parse_category_id_list(value, categories)
                update_product_categories(product_id, category_ids)
            elif choice == "3":
                value = input("새 가격을 입력하세요 > ").strip()
                update_product(product_id, new_price=value)
            elif choice == "4":
                value = input("새 재고를 입력하세요 > ").strip()
                update_product(product_id, new_stock=value)
            else:
                print("오류 : 올바른 메뉴 번호를 입력하세요.")
                continue
            print("상품 정보가 수정되었습니다.")
            return True
        except ValueError as error:
            print(f"오류 : {error}")


def prompt_add_category() -> None:
    while True:
        categories = load_categories()
        print("[카테고리 추가]")
        category_name = input("카테고리명을 입력하세요: ").strip()
        if not is_valid_category_name_text(category_name):
            print("오류 : 카테고리명은 1~10자의 한글이어야 합니다.")
            continue

        parent_category_id = input("상위 카테고리 ID를 입력하세요. 최상위 카테고리로 추가하려면 0을 입력하세요: ").strip()
        if not is_valid_zero_or_numeric_id(parent_category_id):
            print("오류 : 올바른 ID 값을 입력해주세요.")
            continue
        if parent_category_id != "0" and find_category_by_id(categories, parent_category_id) is None:
            print("오류 : 등록되지 않은 카테고리 ID입니다.")
            continue
        if has_sibling_category_name(categories, category_name, parent_category_id):
            print("오류 : 동일한 상위 카테고리에 같은 이름을 사용할 수 없습니다.")
            continue

        categories.append(
            {
                "category_id": get_next_category_id(categories),
                "category_name": normalize_text(category_name),
                "parent_category_id": normalize_text(parent_category_id),
            }
        )
        save_categories(categories)
        print("카테고리가 추가되었습니다.")
        return


def prompt_modify_category() -> None:
    while True:
        categories = load_categories()
        print("[카테고리 수정]")
        category_id = input("수정할 카테고리 ID를 입력하세요: ").strip()
        category = find_category_by_id(categories, category_id)
        if category is None:
            print("오류 : 등록되지 않은 카테고리 ID입니다.")
            continue

        print("1. 카테고리명 수정")
        print("2. 상위 카테고리 수정")
        print("0. 뒤로가기")
        choice = input("선택 > ").strip()
        if choice == "0":
            return
        if choice == "1":
            new_name = input("새 카테고리명을 입력하세요: ").strip()
            if not is_valid_category_name_text(new_name):
                print("오류 : 카테고리명은 1~10자의 한글이어야 합니다.")
                continue
            if has_sibling_category_name(
                categories,
                new_name,
                category["parent_category_id"],
                except_category_id=category_id,
            ):
                print("오류 : 동일한 상위 카테고리에 같은 이름을 사용할 수 없습니다.")
                continue
            category["category_name"] = normalize_text(new_name)
        elif choice == "2":
            new_parent_id = input("새 상위 카테고리 ID를 입력하세요(최상위: 0): ").strip()
            if not is_valid_zero_or_numeric_id(new_parent_id):
                print("오류 : 올바른 ID 값을 입력해주세요.")
                continue
            if new_parent_id == category_id:
                print("오류 : 자기 자신을 상위 카테고리로 지정할 수 없습니다.")
                continue
            if new_parent_id != "0" and find_category_by_id(categories, new_parent_id) is None:
                print("오류 : 등록되지 않은 카테고리 ID입니다.")
                continue
            descendant_ids = get_category_descendant_ids(category_id, categories)
            if new_parent_id in descendant_ids:
                print("오류 : 자기 하위 카테고리를 상위 카테고리로 지정할 수 없습니다.")
                continue
            if has_sibling_category_name(
                categories,
                category["category_name"],
                new_parent_id,
                except_category_id=category_id,
            ):
                print("오류 : 동일한 상위 카테고리에 같은 이름을 사용할 수 없습니다.")
                continue
            category["parent_category_id"] = normalize_text(new_parent_id)
        else:
            print("오류 : 올바른 메뉴 번호를 입력하세요.")
            continue

        save_categories(categories)
        print("카테고리가 수정되었습니다.")
        return


def prompt_delete_category() -> None:
    while True:
        categories = load_categories()
        products = load_products()
        product_categories = load_product_categories(products, categories)
        print("[카테고리 삭제]")
        category_id = input("삭제할 카테고리 ID를 입력하세요: ").strip()
        category = find_category_by_id(categories, category_id)
        if category is None:
            print("오류 : 등록되지 않은 카테고리 ID입니다.")
            continue
        if any(item["parent_category_id"] == category_id for item in categories):
            print("오류 : 하위 카테고리가 있어 삭제할 수 없습니다.")
            return
        if any(item["category_id"] == category_id for item in product_categories):
            print("오류 : 연결된 상품이 있어 삭제할 수 없습니다.")
            return

        confirm = input("정말 삭제하시겠습니까? (Yes/No): ").strip()
        if confirm == "No":
            print("카테고리 삭제를 취소했습니다.")
            return
        if confirm != "Yes":
            print("오류 : Yes 또는 No를 입력하세요.")
            continue

        save_categories([item for item in categories if item["category_id"] != category_id])
        print("카테고리가 삭제되었습니다.")
        return


def admin_category_menu() -> None:
    while True:
        print("[관리자 카테고리 관리]")
        print("1. 카테고리 추가")
        print("2. 카테고리 수정")
        print("3. 카테고리 삭제")
        print("0. 이전 메뉴")
        choice = input("선택 > ").strip()

        if choice == "1":
            prompt_add_category()
        elif choice == "2":
            prompt_modify_category()
        elif choice == "3":
            prompt_delete_category()
        elif choice == "0":
            return
        else:
            print("오류 : 올바른 메뉴 번호를 입력하세요.")


def admin_product_menu() -> None:
    while True:
        products = load_products()
        categories = load_categories()
        product_categories = load_product_categories(products, categories)
        print("[관리자 상품 관리]")
        if products:
            print_product_table(products, build_category_name_map(categories), product_categories)
        else:
            print("등록된 상품이 없습니다.")

        print("1. 상품 등록")
        print("2. 상품 수정")
        print("3. 카테고리 관리")
        print("0. 이전 메뉴")
        choice = input("선택 > ").strip()

        if choice == "1":
            admin_add_product_flow()
        elif choice == "2":
            admin_product_edit_flow()
        elif choice == "3":
            admin_category_menu()
        elif choice == "0":
            return
        else:
            print("오류 : 올바른 메뉴 번호를 입력하세요.")


def admin_order_status_change_flow(order_id: str) -> bool:
    orders = load_orders()
    order_items = load_order_items()
    products = load_products()
    order = find_order_by_order_id(orders, order_id)
    if order is None:
        print("오류 : 등록되지 않은 주문 ID입니다.")
        return False

    print("[관리자 주문 상태 변경]")
    print(f"주문 ID: {order['order_id']}")
    print(f"주문 금액: {format_money(int(order['total_price']))}")
    print(f"주문 상태: {order['order_status']}")
    print("주문 상품:")
    for item in get_order_items_by_order_id(order_items, order_id):
        product = find_product_by_product_id(products, item["product_id"])
        stock_text = "상품 없음" if product is None else f"현재 재고 {product['stock']}개"
        warning = ""
        if product is None or int(item["quantity"]) > int(product["stock"]):
            warning = " / 재고 부족"
        elif product["product_name"] != item["product_name"] or product["price"] != item["price"]:
            warning = " / INFO: 주문 당시 상품 정보와 현재 정보가 다릅니다."
        print(
            f"- {item['product_name']} ({item['quantity']}개, "
            f"{format_money(int(item['price']))}) / {stock_text}{warning}"
        )

    print("1. 주문 승인")
    print("2. 주문 거절")
    print("3. 주문 취소")
    print("0. 이전 메뉴")
    choice = input("주문 변경 번호를 입력하세요 : ").strip()

    action_map = {"1": "approve", "2": "reject", "3": "cancel"}
    if choice == "0":
        return False
    if choice not in action_map:
        print("오류 : 올바른 메뉴 번호를 입력하세요.")
        return False

    try:
        update_order_status_by_admin(order_id, action_map[choice])
        if choice == "1":
            print("주문을 수락합니다.")
        elif choice == "2":
            print("해당 주문을 거절합니다.")
        else:
            print("주문을 취소합니다.")
        return True
    except ValueError as error:
        print(error)
        return False


def admin_order_menu() -> None:
    while True:
        orders = load_orders()
        print("[관리자 주문 관리]")
        if not orders:
            print("등록된 주문이 없습니다.")
        else:
            print("주문 ID | 사용자 ID | 주문 금액 | 주문 상태 | 비고")
            for order in orders:
                note = "재고 부족" if order["order_status"] == "PENDING" and is_order_stock_insufficient(order["order_id"]) else ""
                print(
                    f"{order['order_id']} | {order['user_id']} | "
                    f"{format_money(int(order['total_price']))} | {order['order_status']} | {note}"
                )

        order_id = input("상태 변경할 주문 ID 입력 (0: 이전 메뉴) > ").strip()
        if order_id == "0":
            return
        if not is_valid_numeric_id(order_id):
            print("오류 : 올바른 주문 ID를 입력하세요.")
            continue
        if find_order_by_order_id(orders, order_id) is None:
            print("오류 : 등록되지 않은 주문 ID입니다.")
            continue
        admin_order_status_change_flow(order_id)


# =====================================
# 로그인 / 메인 프롬프트
# =====================================
def prompt_signup() -> None:
    while True:
        print("[회원가입]")
        login_id = input("로그인 ID 입력 (0: 뒤로가기) > ")
        if login_id == "0":
            return
        if login_id.strip() == "":
            print("오류: 로그인 ID는 2~10자의 영문자 또는 숫자여야 합니다.")
            continue
        if has_forbidden_separator(login_id) or not is_valid_login_id(login_id):
            print("오류: 로그인 ID는 2~10자의 영문자 또는 숫자여야 합니다.")
            continue
        if find_user_by_login_id(load_users(), login_id) is not None:
            print("오류: 이미 존재하는 로그인 ID입니다.")
            continue

        password = input("비밀번호 입력 (0: 뒤로가기) > ")
        if password == "0":
            return
        if password.strip() == "" or not is_valid_password(password):
            print("오류: 비밀번호는 2~10자의 영문자 또는 숫자여야 합니다.")
            continue

        name = input("이름 입력 (0: 뒤로가기) > ")
        if name == "0":
            return
        if not is_valid_name(name):
            print("오류: 이름은 1~4자의 한글이어야 합니다.")
            continue

        try:
            user = create_user(login_id, password, name)
            print("회원가입이 완료되었습니다.")
            issue_signup_coupon_if_needed(user["user_id"])
            return
        except ValueError as error:
            print(f"오류: {error}")


def prompt_login() -> None:
    while True:
        print("[로그인]")
        login_id = input("로그인 ID를 입력 (0: 뒤로가기) > ")
        if login_id == "0":
            return
        if login_id.strip() == "":
            print("오류: 로그인 ID는 공백일 수 없습니다.")
            continue
        if not is_valid_login_id(login_id):
            print("오류: 로그인 ID 형식이 올바르지 않습니다.")
            continue

        password = input("비밀번호를 입력 (0: 뒤로가기) > ")
        if password == "0":
            return
        if password.strip() == "":
            print("오류: 비밀번호는 공백일 수 없습니다.")
            continue
        if not is_valid_password(password):
            print("오류: 비밀번호 형식이 올바르지 않습니다.")
            continue

        user = authenticate_user(login_id, password)
        if user is None:
            print("오류: 로그인 ID 또는 비밀번호가 일치하지 않습니다.")
            continue

        print("로그인에 성공했습니다.")
        if user["role"] == "ADMIN":
            print("관리자 계정으로 로그인되었습니다.")
            admin_main_prompt(user)
        else:
            print("일반 사용자 계정으로 로그인되었습니다.")
            user_main_menu_prompt(user)
        return


def prompt_non_login_menu() -> None:
    while True:
        print("[사전 프롬프트]")
        print("1. 로그인")
        print("2. 회원가입")
        print("0. 프로그램 종료")
        choice = input("선택 > ").strip()

        if choice == "0":
            print("프로그램을 종료합니다.")
            return
        if choice == "1":
            prompt_login()
        elif choice == "2":
            prompt_signup()
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


def user_main_menu_prompt(current_user: dict) -> None:
    while True:
        print("[사용자 메인 메뉴]")
        print("1. 상품 조회 / 검색")
        print("2. 장바구니")
        print("3. 주문 관리")
        print("4. 로그아웃")
        choice = input("선택 > ").strip()

        if choice == "1":
            product_search_main_prompt()
        elif choice == "2":
            cart_main_prompt(current_user)
        elif choice == "3":
            order_main_prompt(current_user)
        elif choice == "4":
            print("로그아웃이 완료되었습니다.")
            return
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


def admin_main_prompt(current_user: dict) -> None:
    while True:
        print("[관리자 주 프롬프트]")
        print("1. 상품 관리")
        print("2. 주문 관리")
        print("3. 로그아웃")
        choice = input("선택 > ").strip()

        if choice == "1":
            admin_product_menu()
        elif choice == "2":
            admin_order_menu()
        elif choice == "3":
            print("로그아웃이 완료되었습니다.")
            return
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


def main() -> None:
    initialize_data_files()
    print_initialization_result()
    prompt_non_login_menu()


if __name__ == "__main__":
    main()
