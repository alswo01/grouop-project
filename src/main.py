import re
from datetime import datetime
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

ALL_FILES = [
    USER_FILE,
    PRODUCT_FILE,
    ORDER_FILE,
    ORDER_ITEM_FILE,
    CATEGORY_FILE,
    CART_FILE,
    CART_ITEM_FILE,
]

# =====================================
# 초기 데이터
# =====================================
DEFAULT_ADMIN_RECORD = "1|admin|1234|관리자|ADMIN"

DEFAULT_CATEGORY_RECORDS = [
    "1|식품",
    "2|생활용품",
    "3|주방용품",
    "4|전자제품",
    "5|문구",
    "6|의류",
    "7|기타",
]


# =====================================
# 공통 유틸
# =====================================
def ensure_data_dir() -> None:
    """데이터 폴더가 없으면 생성한다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_file_exists(file_path: Path) -> None:
    """파일이 없으면 빈 파일로 생성한다."""
    if not file_path.exists():
        file_path.write_text("", encoding="utf-8")


def read_lines(file_path: Path) -> list[str]:
    """파일을 읽어 개행을 제거한 줄 목록으로 반환한다."""
    if not file_path.exists():
        return []

    text = file_path.read_text(encoding="utf-8")
    return text.splitlines()


def write_lines(file_path: Path, lines: list[str]) -> None:
    """줄 목록을 파일에 UTF-8로 저장한다."""
    if lines:
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        file_path.write_text("", encoding="utf-8")


# =====================================
# 초기화 로직
# =====================================
def initialize_category_file() -> None:
    """
    category.txt가 비어 있으면 기본 카테고리를 기록한다.
    이미 내용이 있으면 그대로 둔다.
    """
    lines = read_lines(CATEGORY_FILE)

    non_empty_lines = [line for line in lines if line.strip() != ""]
    if not non_empty_lines:
        write_lines(CATEGORY_FILE, DEFAULT_CATEGORY_RECORDS)


def initialize_user_file() -> None:
    """
    user.txt가 비어 있으면 기본 관리자 계정을 기록한다.
    이미 내용이 있으면 그대로 둔다.
    """
    lines = read_lines(USER_FILE)

    non_empty_lines = [line for line in lines if line.strip() != ""]
    if not non_empty_lines:
        write_lines(USER_FILE, [DEFAULT_ADMIN_RECORD])


def initialize_data_files() -> None:
    """데이터 폴더와 전체 데이터 파일을 초기화한다."""
    ensure_data_dir()

    for file_path in ALL_FILES:
        ensure_file_exists(file_path)

    initialize_category_file()
    initialize_user_file()


def print_initialization_result() -> None:
    print("데이터 파일 초기화가 완료되었습니다.")
    print(f"데이터 폴더: {DATA_DIR}")
    print("생성/확인 대상 파일:")
    for file_path in ALL_FILES:
        print(f"- {file_path.name}")


# =====================================
# 정규화 / 검증 함수
# =====================================
def normalize_text(value: str) -> str:
    """문자열 앞뒤 공백을 제거한다."""
    return value.strip()


def is_valid_numeric_id(value: str) -> bool:
    """
    숫자로만 이루어진 길이 1 이상의 ID인지 검사한다.
    선행 0은 허용하지 않는다.
    """
    value = normalize_text(value)

    if value == "":
        return False
    if not value.isdigit():
        return False
    if len(value) > 1 and value.startswith("0"):
        return False
    return True


def is_valid_login_id(value: str) -> bool:
    """
    login_id:
    - 영문자와 숫자만 허용
    - 길이 1~10
    - 앞뒤 공백 제거 후 검사
    """
    value = normalize_text(value)

    if not (1 <= len(value) <= 10):
        return False
    if not re.fullmatch(r"[A-Za-z0-9]+", value):
        return False
    return True


def is_valid_password(value: str) -> bool:
    """
    password:
    - 영문자와 숫자만 허용
    - 길이 1~10
    - 앞뒤 공백 제거 후 검사
    """
    value = normalize_text(value)

    if not (1 <= len(value) <= 10):
        return False
    if not re.fullmatch(r"[A-Za-z0-9]+", value):
        return False
    return True


def is_valid_name(value: str) -> bool:
    """
    name:
    - 한글만 허용
    - 길이 1~4
    - 앞뒤 공백 제거 후 검사
    """
    value = normalize_text(value)

    if not (1 <= len(value) <= 4):
        return False
    if not re.fullmatch(r"[가-힣]+", value):
        return False
    return True


def is_valid_role(value: str) -> bool:
    value = normalize_text(value)
    return value in {"USER", "ADMIN"}


def is_valid_product_name(value: str) -> bool:
    """
    product_name:
    - 길이 1~20
    - 구분자(|, %, &) 포함 불가
    """
    value = normalize_text(value)

    if not (1 <= len(value) <= 20):
        return False
    if "|" in value or "%" in value or "&" in value:
        return False
    return True


def is_valid_price(value: str) -> bool:
    """
    price:
    - 숫자로만 구성
    - 1 이상 1,000,000 이하
    - 선행 0 불허 정책 적용
    """
    value = normalize_text(value)

    if not is_valid_numeric_id(value):
        return False

    num = int(value)
    return 1 <= num <= 1_000_000


def is_valid_stock(value: str) -> bool:
    """
    stock:
    - 숫자로만 구성
    - 0 이상의 정수
    - 0 허용
    """
    value = normalize_text(value)

    if value == "":
        return False
    if not value.isdigit():
        return False
    if len(value) > 1 and value.startswith("0"):
        return False

    num = int(value)
    return num >= 0


def is_valid_quantity(value: str) -> bool:
    """
    quantity:
    - 숫자로만 구성
    - 1 이상의 정수
    """
    value = normalize_text(value)

    if not is_valid_numeric_id(value):
        return False

    num = int(value)
    return num >= 1


def is_valid_order_status(value: str) -> bool:
    value = normalize_text(value)
    return value in {
        "PENDING",
        "ACCEPTED",
        "REJECTED",
        "CANCEL_REQUESTED",
        "CANCELLED",
    }


def is_valid_category_id(value: str) -> bool:
    value = normalize_text(value)
    return value in {"1", "2", "3", "4", "5", "6", "7"}


def is_valid_category_name(value: str) -> bool:
    value = normalize_text(value)
    return value in {"식품", "생활용품", "주방용품", "전자제품", "문구", "의류", "기타"}


def is_valid_order_time(value: str) -> bool:
    """
    order_time:
    - YYMMDDHHMMSS 형식
    - 12자리 숫자
    - 실제 존재하는 날짜/시간
    """
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


# =====================================
# 레코드 파싱 / 직렬화 함수
# =====================================
def split_record(line: str, expected_count: int) -> list[str] | None:
    """
    한 줄을 | 기준으로 분리한다.
    필드 개수가 기대값과 다르면 None을 반환한다.
    """
    parts = line.split("|")
    if len(parts) != expected_count:
        return None
    return parts


def serialize_record(values: list[str]) -> str:
    """
    문자열 필드 목록을 | 로 연결해 한 줄 레코드로 만든다.
    """
    return "|".join(values)


def parse_user_record(line: str) -> dict | None:
    """
    user.txt의 한 줄을 파싱한다.
    형식이 맞지 않으면 None 반환.
    """
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
    """
    product.txt의 한 줄을 파싱한다.
    형식이 맞지 않으면 None 반환.
    """
    parts = split_record(line, 5)
    if parts is None:
        return None

    product_id, category_id, product_name, price, stock = parts

    if not is_valid_numeric_id(product_id):
        return None
    if not is_valid_category_id(category_id):
        return None
    if not is_valid_product_name(product_name):
        return None
    if not is_valid_price(price):
        return None
    if not is_valid_stock(stock):
        return None

    return {
        "product_id": normalize_text(product_id),
        "category_id": normalize_text(category_id),
        "product_name": normalize_text(product_name),
        "price": normalize_text(price),
        "stock": normalize_text(stock),
    }


def parse_cart_record(line: str) -> dict | None:
    """
    cart.txt의 한 줄을 파싱한다.
    형식이 맞지 않으면 None 반환.
    """
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
    """
    cart_item.txt의 한 줄을 파싱한다.
    형식이 맞지 않으면 None 반환.
    """
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
    parts = split_record(line, 5)
    if parts is None:
        return None

    order_id, user_id, total_price, order_status, order_time = parts

    if not is_valid_numeric_id(order_id):
        return None
    if not is_valid_numeric_id(user_id):
        return None
    if not is_valid_price(total_price):
        return None
    if not is_valid_order_status(order_status):
        return None
    if not is_valid_order_time(order_time):
        return None

    return {
        "order_id": normalize_text(order_id),
        "user_id": normalize_text(user_id),
        "total_price": normalize_text(total_price),
        "order_status": normalize_text(order_status),
        "order_time": normalize_text(order_time),
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

    return deduplicate_products(products)


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
        carts = filter_valid_carts(carts, users)

    return carts


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
        cart_items = filter_valid_cart_items(cart_items, carts, products)
        cart_items, duplicate_found = merge_duplicate_cart_products(cart_items)

        if duplicate_found:
            print("[WARNING] 동일 장바구니 내 중복 상품이 발견되어 수량을 합산하였습니다.")

        if check_cart_stock_warnings(cart_items, products):
            print("[WARNING] 장바구니에 담긴 상품 수량이 현재 재고를 초과하는 항목이 있습니다.")

    return cart_items


# =====================================
# 파일 저장 함수
# =====================================
def save_users(users: list[dict]) -> None:
    lines = [
        serialize_record([
            user["user_id"],
            user["login_id"],
            user["password"],
            user["name"],
            user["role"],
        ])
        for user in users
    ]
    write_lines(USER_FILE, lines)


def save_products(products: list[dict]) -> None:
    lines = [
        serialize_record([
            product["product_id"],
            product["category_id"],
            product["product_name"],
            product["price"],
            product["stock"],
        ])
        for product in products
    ]
    write_lines(PRODUCT_FILE, lines)


def save_carts(carts: list[dict]) -> None:
    lines = [
        serialize_record([
            cart["cart_id"],
            cart["user_id"],
        ])
        for cart in carts
    ]
    write_lines(CART_FILE, lines)


def save_cart_items(cart_items: list[dict]) -> None:
    lines = [
        serialize_record([
            item["cart_item_id"],
            item["cart_id"],
            item["product_id"],
            item["quantity"],
        ])
        for item in cart_items
    ]
    write_lines(CART_ITEM_FILE, lines)


def deduplicate_orders(orders: list[dict]) -> list[dict]:
    result = []
    seen_order_ids = set()

    for order in orders:
        if order["order_id"] in seen_order_ids:
            continue
        seen_order_ids.add(order["order_id"])
        result.append(order)

    return result


def deduplicate_order_items(order_items: list[dict]) -> list[dict]:
    result = []
    seen_order_item_ids = set()

    for item in order_items:
        if item["order_item_id"] in seen_order_item_ids:
            continue
        seen_order_item_ids.add(item["order_item_id"])
        result.append(item)

    return result


def load_orders() -> list[dict]:
    orders = []

    for line in read_lines(ORDER_FILE):
        if normalize_text(line) == "":
            continue

        record = parse_order_record(line)
        if record is not None:
            orders.append(record)

    return deduplicate_orders(orders)


def load_order_items() -> list[dict]:
    order_items = []

    for line in read_lines(ORDER_ITEM_FILE):
        if normalize_text(line) == "":
            continue

        record = parse_order_item_record(line)
        if record is not None:
            order_items.append(record)

    return deduplicate_order_items(order_items)


def save_orders(orders: list[dict]) -> None:
    lines = [
        serialize_record([
            order["order_id"],
            order["user_id"],
            order["total_price"],
            order["order_status"],
            order["order_time"],
        ])
        for order in orders
    ]
    write_lines(ORDER_FILE, lines)


def save_order_items(order_items: list[dict]) -> None:
    lines = [
        serialize_record([
            item["order_item_id"],
            item["order_id"],
            item["product_id"],
            item["product_name"],
            item["price"],
            item["quantity"],
        ])
        for item in order_items
    ]
    write_lines(ORDER_ITEM_FILE, lines)


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


def find_cart_by_cart_id(carts: list[dict], cart_id: str) -> dict | None:
    cart_id = normalize_text(cart_id)
    for cart in carts:
        if cart["cart_id"] == cart_id:
            return cart
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


def get_order_items_by_order_id(order_items: list[dict], order_id: str) -> list[dict]:
    order_id = normalize_text(order_id)
    return [item for item in order_items if item["order_id"] == order_id]


# =====================================
# 무결성 검사 / 정리 함수 (1차)
# =====================================
def deduplicate_users(users: list[dict]) -> list[dict]:
    result = []
    seen_user_ids = set()
    seen_login_ids = set()

    for user in users:
        user_id = user["user_id"]
        login_id = user["login_id"].upper()

        if user_id in seen_user_ids:
            continue
        if login_id in seen_login_ids:
            continue

        seen_user_ids.add(user_id)
        seen_login_ids.add(login_id)
        result.append(user)

    return result


def deduplicate_products(products: list[dict]) -> list[dict]:
    result = []
    seen_product_ids = set()

    for product in products:
        product_id = product["product_id"]
        if product_id in seen_product_ids:
            continue

        seen_product_ids.add(product_id)
        result.append(product)

    return result


def deduplicate_carts(carts: list[dict]) -> list[dict]:
    result = []
    seen_cart_ids = set()
    seen_user_ids = set()

    for cart in carts:
        cart_id = cart["cart_id"]
        user_id = cart["user_id"]

        if cart_id in seen_cart_ids:
            continue
        if user_id in seen_user_ids:
            continue

        seen_cart_ids.add(cart_id)
        seen_user_ids.add(user_id)
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


# =====================================
# 참조 무결성 검사 함수
# =====================================
def filter_valid_carts(carts: list[dict], users: list[dict]) -> list[dict]:
    """
    cart의 user_id가 실제 users에 존재하는 경우만 남긴다.
    """
    valid_user_ids = {user["user_id"] for user in users}
    result = []

    for cart in carts:
        if cart["user_id"] in valid_user_ids:
            result.append(cart)

    return result


def filter_valid_cart_items(
    cart_items: list[dict],
    carts: list[dict],
    products: list[dict],
) -> list[dict]:
    """
    cart_item의 cart_id, product_id가 실제 존재하는 경우만 남긴다.
    """
    valid_cart_ids = {cart["cart_id"] for cart in carts}
    valid_product_ids = {product["product_id"] for product in products}
    result = []

    for item in cart_items:
        if item["cart_id"] not in valid_cart_ids:
            continue
        if item["product_id"] not in valid_product_ids:
            continue
        result.append(item)

    return result


def merge_duplicate_cart_products(cart_items: list[dict]) -> tuple[list[dict], bool]:
    """
    같은 cart_id 안에서 동일한 product_id가 여러 번 등장하면
    quantity를 합산하여 하나의 레코드로 정리한다.

    반환값:
    - 정리된 cart_items
    - 중복 합산이 발생했는지 여부
    """
    merged_map = {}
    duplicate_found = False

    for item in cart_items:
        key = (item["cart_id"], item["product_id"])

        if key not in merged_map:
            merged_map[key] = {
                "cart_item_id": item["cart_item_id"],
                "cart_id": item["cart_id"],
                "product_id": item["product_id"],
                "quantity": item["quantity"],
            }
        else:
            duplicate_found = True
            old_qty = int(merged_map[key]["quantity"])
            new_qty = int(item["quantity"])
            merged_map[key]["quantity"] = str(old_qty + new_qty)

    merged_items = list(merged_map.values())
    return merged_items, duplicate_found


def check_cart_stock_warnings(
    cart_items: list[dict],
    products: list[dict],
) -> bool:
    """
    장바구니 수량이 상품 재고를 초과하는 항목이 하나라도 있으면 True 반환.
    """
    product_stock_map = {product["product_id"]: int(product["stock"]) for product in products}

    for item in cart_items:
        product_id = item["product_id"]
        quantity = int(item["quantity"])
        stock = product_stock_map.get(product_id, 0)

        if quantity > stock:
            return True

    return False


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

    new_user = {
        "user_id": get_next_user_id(users),
        "login_id": normalize_text(login_id),
        "password": normalize_text(password),
        "name": normalize_text(name),
        "role": "USER",
    }

    users.append(new_user)
    save_users(users)
    return new_user


def authenticate_user(login_id: str, password: str) -> dict | None:
    users = load_users()

    if not is_valid_login_id(login_id):
        return None
    if not is_valid_password(password):
        return None

    user = find_user_by_login_id(users, login_id)
    if user is None:
        return None

    if user["password"] != normalize_text(password):
        return None

    return user


# =====================================
# 상품 서비스 함수
# =====================================
def find_product_by_name(products: list[dict], product_name: str) -> dict | None:
    target = normalize_text(product_name)
    for product in products:
        if product["product_name"] == target:
            return product
    return None


def create_product(category_id: str, product_name: str, price: str, stock: str) -> dict:
    products = load_products()

    if not is_valid_category_id(category_id):
        raise ValueError("카테고리 ID가 올바르지 않습니다.")
    if not is_valid_product_name(product_name):
        raise ValueError("상품명 형식이 올바르지 않습니다.")
    if not is_valid_price(price):
        raise ValueError("가격 형식이 올바르지 않습니다.")
    if not is_valid_stock(stock):
        raise ValueError("재고 형식이 올바르지 않습니다.")

    if find_product_by_name(products, product_name) is not None:
        raise ValueError("이미 존재하는 상품명입니다.")

    new_product = {
        "product_id": get_next_product_id(products),
        "category_id": normalize_text(category_id),
        "product_name": normalize_text(product_name),
        "price": normalize_text(price),
        "stock": normalize_text(stock),
    }

    products.append(new_product)
    save_products(products)
    return new_product


# =====================================
# 수정 공통 함수
# =====================================
def update_product(
    product_id: str,
    *,
    new_category_id: str | None = None,
    new_product_name: str | None = None,
    new_price: str | None = None,
    new_stock: str | None = None,
) -> dict:
    products = load_products()
    product = find_product_by_product_id(products, product_id)

    if product is None:
        raise ValueError("존재하지 않는 상품입니다.")

    if new_category_id is not None:
        if not is_valid_category_id(new_category_id):
            raise ValueError("카테고리 ID가 올바르지 않습니다.")
        product["category_id"] = normalize_text(new_category_id)

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


def parse_order_record(line: str) -> dict | None:
    parts = split_record(line, 5)
    if parts is None:
        return None

    order_id, user_id, total_price, order_status, order_time = parts

    if not is_valid_numeric_id(order_id):
        return None
    if not is_valid_numeric_id(user_id):
        return None
    if not is_valid_price(total_price):
        return None
    if not is_valid_order_status(order_status):
        return None
    if not is_valid_order_time(order_time):
        return None

    return {
        "order_id": normalize_text(order_id),
        "user_id": normalize_text(user_id),
        "total_price": normalize_text(total_price),
        "order_status": normalize_text(order_status),
        "order_time": normalize_text(order_time),
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


# =====================================
# ID 생성 함수
# =====================================
def get_next_numeric_id(records: list[dict], key: str) -> str:
    """
    records 안의 key 값을 기준으로 다음 숫자 ID를 문자열로 반환한다.
    records가 비어 있으면 "1" 반환.
    """
    if not records:
        return "1"

    max_id = max(int(record[key]) for record in records)
    return str(max_id + 1)


def get_next_user_id(users: list[dict]) -> str:
    return get_next_numeric_id(users, "user_id")


def get_next_product_id(products: list[dict]) -> str:
    return get_next_numeric_id(products, "product_id")


def get_next_cart_id(carts: list[dict]) -> str:
    return get_next_numeric_id(carts, "cart_id")


def get_next_cart_item_id(cart_items: list[dict], cart_id: str) -> str:
    """
    같은 cart_id 안에서만 cart_item_id를 증가시킨다.
    해당 cart에 아이템이 없으면 "1" 반환.
    """
    same_cart_items = [item for item in cart_items if item["cart_id"] == cart_id]

    if not same_cart_items:
        return "1"

    max_id = max(int(item["cart_item_id"]) for item in same_cart_items)
    return str(max_id + 1)


def get_next_order_id(orders: list[dict]) -> str:
    return get_next_numeric_id(orders, "order_id")


def get_next_order_item_id(order_items: list[dict]) -> str:
    return get_next_numeric_id(order_items, "order_item_id")


# =====================================
# 카트 생성 / 조회 함수
# =====================================
def get_or_create_cart(user_id: str) -> dict:
    """
    user_id에 해당하는 cart를 반환한다.
    없으면 새 cart를 생성하고 저장한 뒤 반환한다.
    """
    users = load_users()
    user = find_user_by_user_id(users, user_id)
    if user is None:
        raise ValueError("존재하지 않는 사용자 ID입니다.")

    carts = load_carts(users)
    cart = find_cart_by_user_id(carts, user_id)

    if cart is not None:
        return cart

    new_cart = {
        "cart_id": get_next_cart_id(carts),
        "user_id": normalize_text(user_id),
    }

    carts.append(new_cart)
    save_carts(carts)
    return new_cart


def add_product_to_cart(user_id: str, product_id: str, quantity: str) -> None:
    """
    사용자의 장바구니에 상품을 추가한다.
    같은 상품이 이미 있으면 quantity를 증가시킨다.
    """
    users = load_users()
    products = load_products()

    user = find_user_by_user_id(users, user_id)
    if user is None:
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

    # 이미 같은 상품이 장바구니에 있는지 확인
    for item in cart_items:
        if item["cart_id"] == cart["cart_id"] and item["product_id"] == normalize_text(product_id):
            new_quantity = int(item["quantity"]) + int(quantity)
            item["quantity"] = str(new_quantity)
            save_cart_items(cart_items)

            if new_quantity > int(product["stock"]):
                print("[WARNING] 장바구니에 담긴 상품 수량이 현재 재고를 초과하는 항목이 있습니다.")
            return

    # 없으면 새 cart_item 생성
    new_item = {
        "cart_item_id": get_next_cart_item_id(cart_items, cart["cart_id"]),
        "cart_id": cart["cart_id"],
        "product_id": normalize_text(product_id),
        "quantity": normalize_text(quantity),
    }

    cart_items.append(new_item)
    save_cart_items(cart_items)

    if int(quantity) > int(product["stock"]):
        print("[WARNING] 장바구니에 담긴 상품 수량이 현재 재고를 초과하는 항목이 있습니다.")


def remove_product_from_cart(user_id: str, product_id: str) -> None:
    """
    사용자의 장바구니에서 특정 product_id 항목 전체를 삭제한다.
    """
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)

    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        raise ValueError("장바구니가 존재하지 않습니다.")

    target_index = None
    for index, item in enumerate(cart_items):
        if item["cart_id"] == cart["cart_id"] and item["product_id"] == normalize_text(product_id):
            target_index = index
            break

    if target_index is None:
        raise ValueError("장바구니에 존재하지 않는 상품입니다.")

    del cart_items[target_index]
    save_cart_items(cart_items)


def get_cart_items_for_user(user_id: str) -> list[dict]:
    """
    특정 사용자의 장바구니 아이템 목록을 반환한다.
    """
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)

    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        return []

    return [item for item in cart_items if item["cart_id"] == cart["cart_id"]]

# =====================================
# 장바구니 화면 보조 함수
# =====================================
def format_money(value: int) -> str:
    return f"{value}원"


def build_cart_view_rows(user_id: str) -> list[dict]:
    """
    현재 사용자의 Cart_Item과 Product를 product_id 기준으로 결합해
    장바구니 조회 화면용 데이터를 만든다.
    """
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
        item_total = price * quantity

        rows.append({
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": price,
            "quantity": quantity,
            "item_total": item_total,
            "stock": stock,
            "stock_text": "품절" if stock == 0 else f"{stock}개",
            "stock_warning": quantity > stock,
        })

    rows.sort(key=lambda x: int(x["product_id"]))
    return rows


def print_cart_view(user_id: str) -> None:
    """
    장바구니 조회 결과를 출력한다.
    """
    try:
        rows = build_cart_view_rows(user_id)
    except Exception:
        print("오류: 장바구니 정보를 불러오지 못했습니다.")
        return

    print("[장바구니 조회]")

    if not rows:
        print("장바구니가 비어 있습니다.")
        return

    total_types = len(rows)
    total_price = sum(row["item_total"] for row in rows)

    print(f"총 상품 종류: {total_types}개")
    print(f"총 금액: {format_money(total_price)}")
    print("------------------------------")

    for idx, row in enumerate(rows, start=1):
        print(f"[{idx}]")
        print(f"상품 ID: {row['product_id']}")
        print(f"상품명: {row['product_name']}")
        print(f"가격: {format_money(row['price'])}")
        print(f"수량: {row['quantity']}개")
        print(f"상품 합계: {format_money(row['item_total'])}")
        print(f"재고: {row['stock_text']}")
        if row["stock_warning"]:
            print("재고 경고: 현재 재고보다 많이 담겨 있습니다.")
        print("------------------------------")


# =====================================
# 장바구니 부 프롬프트 함수
# =====================================
def prompt_add_product_to_cart(current_user: dict) -> None:
    user_id = current_user["user_id"]

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
            product = find_product_by_product_id(load_products(), product_id)
            if product is None:
                print("오류: 존재하지 않는 상품입니다.")
                continue

            if int(product["stock"]) == 0:
                print("오류: 품절 상품은 장바구니에 담을 수 없습니다.")
                continue

            add_product_to_cart(user_id, product_id, quantity)
            print("상품이 장바구니에 추가되었습니다.")

            rows = build_cart_view_rows(user_id)
            for row in rows:
                if row["product_id"] == product_id and row["stock_warning"]:
                    print("경고: 현재 재고보다 많이 담겨 있습니다. 실제 주문 가능 여부는 주문 시 확인됩니다.")
                    break
            return

        except ValueError as e:
            print(f"오류: {e}")
            return
        except Exception:
            print("오류: 장바구니를 저장하지 못했습니다.")
            return


def prompt_remove_product_from_cart(current_user: dict) -> None:
    user_id = current_user["user_id"]

    while True:
        print("[상품 삭제]")
        product_id = input("삭제할 상품 ID 입력 > ").strip()

        if not is_valid_numeric_id(product_id):
            print("오류: 장바구니에 존재하지 않는 상품입니다.")
            continue

        try:
            product = find_product_by_product_id(load_products(), product_id)
            if product is None:
                print("오류: 존재하지 않는 상품입니다.")
                continue

            remove_product_from_cart(user_id, product_id)
            print("상품이 장바구니에서 삭제되었습니다.")
            return

        except ValueError as e:
            message = str(e)
            if "장바구니에 존재하지 않는 상품" in message:
                print("오류: 장바구니에 존재하지 않는 상품입니다.")
                continue
            print(f"오류: {message}")
            return
        except Exception:
            print("오류: 장바구니를 저장하지 못했습니다.")
            return


# =====================================
# 장바구니 주 프롬프트 함수
# =====================================
def cart_main_prompt(current_user: dict) -> None:
    user_id = current_user["user_id"]

    try:
        get_or_create_cart(user_id)
    except Exception:
        print("오류: 장바구니 정보를 불러오지 못했습니다.")
        return

    while True:
        print("[장바구니 메뉴]")
        print("1. 장바구니 조회")
        print("2. 상품 추가")
        print("3. 상품 삭제")
        print("0. 이전 메뉴")

        choice = input("선택 > ").strip()

        if choice == "1":
            print_cart_view(user_id)
        elif choice == "2":
            prompt_add_product_to_cart(current_user)
        elif choice == "3":
            prompt_remove_product_from_cart(current_user)
        elif choice == "0":
            return
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


# =====================================
# 주문 생성 함수
# =====================================
def get_current_order_time() -> str:
    return datetime.now().strftime("%y%m%d%H%M%S")


def create_order_from_cart(user_id: str) -> dict:
    users = load_users()
    products = load_products()
    carts = load_carts(users)
    cart_items = load_cart_items(carts, products)
    orders = load_orders()
    order_items = load_order_items()

    user = find_user_by_user_id(users, user_id)
    if user is None:
        raise ValueError("존재하지 않는 사용자입니다.")

    cart = find_cart_by_user_id(carts, user_id)
    if cart is None:
        raise ValueError("장바구니가 비어 있습니다.")

    user_cart_items = [item for item in cart_items if item["cart_id"] == cart["cart_id"]]
    if not user_cart_items:
        raise ValueError("장바구니가 비어 있습니다.")

    total_price = 0

    # 재고 선검증 + 총액 계산
    for item in user_cart_items:
        product = find_product_by_product_id(products, item["product_id"])
        if product is None:
            raise ValueError("유효하지 않은 상품이 장바구니에 있습니다.")

        if int(item["quantity"]) > int(product["stock"]):
            raise ValueError("재고가 부족한 상품이 포함되어 있습니다.")

        total_price += int(product["price"]) * int(item["quantity"])

    if total_price > 1_000_000:
        raise ValueError("총 주문 금액은 1,000,000원을 초과할 수 없습니다.")

    new_order = {
        "order_id": get_next_order_id(orders),
        "user_id": normalize_text(user_id),
        "total_price": str(total_price),
        "order_status": "PENDING",
        "order_time": get_current_order_time(),
    }
    orders.append(new_order)

    next_order_item_id = get_next_order_item_id(order_items)

    for item in user_cart_items:
        product = find_product_by_product_id(products, item["product_id"])

        order_items.append({
            "order_item_id": next_order_item_id,
            "order_id": new_order["order_id"],
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "quantity": item["quantity"],
        })
        next_order_item_id = str(int(next_order_item_id) + 1)

    # 주문 성공 후 장바구니 비우기
    remaining_cart_items = [
        item for item in cart_items
        if item["cart_id"] != cart["cart_id"]
    ]

    save_orders(orders)
    save_order_items(order_items)
    save_cart_items(remaining_cart_items)

    return new_order


# =====================================
# 주문 상태 관련 서비스 함수
# =====================================
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


# =====================================
# 재고 부족 판단 함수
# =====================================
def is_order_stock_insufficient(order_id: str) -> bool:
    products = load_products()
    order_items = load_order_items()

    items = get_order_items_by_order_id(order_items, order_id)

    for item in items:
        product = find_product_by_product_id(products, item["product_id"])
        if product is None:
            return True

        if int(product["stock"]) == 0:
            return True

        if int(item["quantity"]) > int(product["stock"]):
            return True

    return False


# =====================================
# 관리자 주문 처리 함수
# =====================================
def update_order_status_by_admin(order_id: str, action: str) -> dict:
    """
    action:
    - "approve"  : 주문 승인
    - "reject"   : 주문 거절
    - "cancel"   : 주문 취소 완료
    """
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

        items = get_order_items_by_order_id(order_items, order_id)

        for item in items:
            product = find_product_by_product_id(products, item["product_id"])
            product["stock"] = str(int(product["stock"]) - int(item["quantity"]))

        order["order_status"] = "ACCEPTED"
        save_products(products)
        save_orders(orders)
        return order

    elif action == "reject":
        if order["order_status"] != "PENDING":
            raise ValueError("처리가 완료된 주문입니다.")

        if not is_order_stock_insufficient(order_id):
            raise ValueError("거절 가능한 주문이 아닙니다.")

        order["order_status"] = "REJECTED"
        save_orders(orders)
        return order

    elif action == "cancel":
        if order["order_status"] != "CANCEL_REQUESTED":
            raise ValueError("취소 가능한 주문이 아닙니다.")

        order["order_status"] = "CANCELLED"
        save_orders(orders)
        return order

    else:
        raise ValueError("지원하지 않는 관리자 주문 처리 동작입니다.")
    
# =====================================
# 회원가입 부 프롬프트 함수
# =====================================
def prompt_signup() -> None:
    while True:
        print("[회원가입]")

        login_id = input("로그인 ID 입력 (0: 뒤로가기) > ")
        if login_id == "0":
            return
        if login_id.strip() == "":
            print("오류: 로그인 ID는 1~10자의 영문자 또는 숫자여야 합니다.")
            continue
        if any(ch in login_id for ch in "|%&"):
            print("오류: 로그인 ID에는 특수문자를 사용할 수 없습니다.")
            continue
        if not is_valid_login_id(login_id.strip()):
            print("오류: 로그인 ID는 1~10자의 영문자 또는 숫자여야 합니다.")
            continue

        users = load_users()
        if find_user_by_login_id(users, login_id.strip()) is not None:
            print("오류: 이미 존재하는 로그인 ID입니다.")
            continue

        password = input("비밀번호 입력 (0: 뒤로가기) > ")
        if password == "0":
            return
        if password.strip() == "":
            print("오류: 비밀번호는 1~10자의 영문자 또는 숫자여야 합니다.")
            continue
        if not is_valid_password(password.strip()):
            print("오류: 비밀번호는 1~10자의 영문자 또는 숫자여야 합니다.")
            continue

        name = input("이름 입력 (0: 뒤로가기) > ")
        if name == "0":
            return
        if name.strip() == "":
            print("오류: 이름은 1~4자의 한글이어야 합니다.")
            continue
        if not is_valid_name(name.strip()):
            print("오류: 이름은 1~4자의 한글이어야 합니다.")
            continue

        try:
            create_user(login_id.strip(), password.strip(), name.strip())
            print("회원가입이 완료되었습니다.")
            return
        except ValueError as e:
            print(f"오류: {e}")


# =====================================
# 로그인 부 프롬프트 함수
# =====================================
def prompt_login() -> None:
    while True:
        print("[로그인]")

        login_id = input("로그인 ID를 입력 (0: 뒤로가기) > ")
        if login_id == "0":
            return
        if login_id.strip() == "":
            print("오류: 로그인 ID는 공백일 수 없습니다.")
            continue
        if not is_valid_login_id(login_id.strip()):
            print("오류: 로그인 ID 형식이 올바르지 않습니다.")
            continue

        password = input("비밀번호를 입력 (0: 뒤로가기) > ")
        if password == "0":
            return
        if password.strip() == "":
            print("오류: 비밀번호는 공백일 수 없습니다.")
            continue
        if not is_valid_password(password.strip()):
            print("오류: 비밀번호 형식이 올바르지 않습니다.")
            continue

        user = authenticate_user(login_id.strip(), password.strip())
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


# =====================================
# 비로그인 상태 주 프롬프트 함수
# =====================================
def prompt_non_login_menu() -> None:
    while True:
        print("[사전 프롬프트]")
        print("1. 로그인")
        print("2. 회원가입")
        print("0. 프로그램 종료")

        choice = input("선택 > ").strip()

        if choice == "0":
            print("프로그램을 종료합니다.")
            break
        elif choice == "1":
            prompt_login()
        elif choice == "2":
            prompt_signup()
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


# =====================================
# 사용자 메인 메뉴 주 프롬프트 함수
# =====================================
def user_main_menu_prompt(current_user: dict) -> None:
    while True:
        print("[사용자 메인 메뉴]")
        print("1. 상품 조회 / 검색")
        print("2. 장바구니")
        print("3. 주문 관리")
        print("4. 로그아웃")

        choice = input("선택 > ").strip()

        if choice == "1":
            print("상품 조회 / 검색 기능은 아직 구현 전입니다.")
        elif choice == "2":
            cart_main_prompt(current_user)
        elif choice == "3":
            print("주문 관리 기능은 아직 구현 전입니다.")
        elif choice == "4":
            print("로그아웃이 완료되었습니다.")
            return
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


# =====================================
# 관리자 주 프롬프트 함수
# =====================================
def admin_main_prompt(current_user: dict) -> None:
    while True:
        print("[관리자 주 프롬프트]")
        print("1. 상품 관리")
        print("2. 주문 관리")
        print("3. 로그아웃")

        choice = input("선택 > ").strip()

        if choice == "1":
            print("상품 관리 기능은 아직 구현 전입니다.")
        elif choice == "2":
            print("주문 관리 기능은 아직 구현 전입니다.")
        elif choice == "3":
            print("로그아웃이 완료되었습니다.")
            return
        else:
            if choice.isdigit():
                print("오류: 올바른 메뉴 번호를 입력하세요.")
            else:
                print("오류: 숫자만 입력 가능합니다.")


# =====================================
# 메인 실행 함수
# =====================================
def main() -> None:
    initialize_data_files()
    print_initialization_result()
    prompt_non_login_menu()


if __name__ == "__main__":
    main()