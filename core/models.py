class User:
    def __init__(self, uname, phno, email, role):
        self.profile = Profile(uname, phno, email)
        self.role = role.lower()

    def customer_flow(self, product_list):
        cart = Cart()

        while True:
            print("\n1. View Products\n2. Add to Cart\n3. View Cart\n4. Pay\n5. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                for p in product_list:
                    p.display()
                    print("-"*30)

            elif choice == "2":
                pid = int(input("Enter Product ID: "))
                qty = int(input("Enter Product Quantity: "))
                product = None
                for p in product_list:
                    if p.id == pid:
                        product = p
                        break
                if product:
                    cart.add_item(product, qty)
                else:
                    print("❌ Product not found")

            elif choice == "3":
                cart.view_cart()

            elif choice == "4":
                total = cart.total()
                print(f"Total Amount: {total}")
                payment = Payment(total)
                payment.pay()

            elif choice == "5":
                print("Exiting customer mode")
                break
            else:
                print("Invalid Choice")


class Product:
    def __init__(self, id, name, price, category, description, stock):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.stock = stock

    def display(self):
        print(f"Product id: {self.id}")
        print(f"Product Name: {self.name}")
        print(f"Product Price: {self.price}")
        print(f"Product category: {self.category}")
        print(f"Product Desciption: {self.description}")
        print(f"Product Stocks: {self.stock}")

    def update_stock(self, quantity):
        if quantity <= self.stock:
            self.stock -= quantity
            return True
        else:
            print("Insufficient Stocks📉")
            return False

    @staticmethod
    def add_product(product_list):
        print("\n=== Add New Products ===")
        id = len(product_list)+1
        name = input("Product Name: ")
        price = float(input("Product Price: "))
        category = input("Category: ")
        description = input("Description: ")
        stock = int(input("Stock: "))

        new_product = Product(id, name, price, category, description, stock)
        product_list.append(new_product)
        print("Product Added Successfully!! ")


class Profile:
    def __init__(self, uname, phno, email, address=""):
        self.uname = uname
        self.phno = phno
        self.email = email
        self.address = address

    def display_profile(self):
        print(f"Username: {self.uname}")
        print(f"Phone Number: {self.phno}")
        print(f"Email: {self.email}")
        print(f"Address: {self.address}")

    def edit_profile(self):
        print("Edit Profile")
        self.uname = input("Enter Username: ") or self.uname
        self.phno = input("Enter Phone Number: ") or self.phno
        self.email = input("Enter Email ID: ") or self.email
        print("Profile Updated Successfully")

    def add_address(self):
        self.address = input("Enter Address: ")
        print("Address Added Successfully!!")


class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, qty):
        self.items.append((product, qty))

    def remove_item(self, product):
        new_items = []
        for p, q in self.items:
            if p != product:
                new_items.append((p, q))
        self.items = new_items

    def view_cart(self):
        for p, q in self.items:
            print(f"{p.name} x{q} = ₹{p.price * q}")

    def total(self):
        total = 0
        for product, qty in self.items:
            total += product.price * qty
        return total


class Payment:
    def __init__(self, total_amount):
        self.total_amount = total_amount
        self.balance = 50000
        print("\n=== Payment Options ===")
        print("1. Debit Card")
        print("2. Credit Card")
        print("3. Cash on Delivery")
        print("4. Net Banking")

    def pay(self):
        options = int(input("Enter an option(1-4): "))
        if options == 1:
            print("Debit Card Payment: ")
            self.debit_card()

        elif options == 2:
            print("Credit Card: ")
            self.credit_card()

        elif options == 3:
            print("Cash on Delivery: ")
            self.cod()
        elif options == 4:
            print("Netbanking")
            self.net_banking()
        else:
            print("❌Invalid option, please choose an option between 1-4")

    def verify_payment(self):
        if self.balance >= self.total_amount:
            self.balance -= self.total_amount
            return True
        else:
            return False

    def debit_card(self):
        print("Debit Card Payment")
        cname = input("Enter Customer Name: ")
        card_no = input("Enter Card Number: ")
        cvv = input("Enter CVV Number: ")

        if self.verify_payment():
            print(
                f"Payment Successful {self.total_amount} paid through your account")
        else:
            print("Insufficient Balance, Payment Failed")

    def credit_card(self):
        print("Credit Card Payment")
        cname = input("Enter Customer Name: ")
        card_no = input("Enter Card Number: ")
        cvv = input("Enter CVV Number: ")

        if self.verify_payment():
            print(
                f"Payment Successful {self.total_amount} paid through your account")
        else:
            print("Insufficient Balance, Payment Failed")

    def cod(self):
        print("Enter Details")
        address = input("Enter adress: ")
        pincode = int(input("Enter Pincode: "))
        print(f"order will be delivered to: {address}")

    def net_banking(self):
        print("Net Banking Details")
        bank = input("Enter Bank Name: ")
        username = input("Enter username: ")
        password = input("Enter Password: ")

        if self.verify_payment():
            print(
                f"Payment Successful {self.total_amount} paid through your account")
        else:
            print("Insufficient Balance, Payment Failed")


product_list = []


def main():
    print("==== Welcome to the Shopping App ====")
    role = input("Enter Your Role (Seller/Customer): ").strip().lower()
    uname = input("Enter Name: ")
    phno = input("Enter Phone Number: ")
    email = input("Enter Email ID: ")

    user = User(uname, phno, email, role)

    if user.role == "seller":
        while True:
            print("\n1. Add Product\n2. View All Products\n3. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                Product.add_product(product_list)
            elif choice == "2":
                for p in product_list:
                    p.display()
                    print("-" * 30)
            elif choice == "3":
                print("Exiting seller mode.")
                break
            else:
                print("❌ Invalid choice")

    elif user.role == "customer":
        if not product_list:
            print(
                "No Products Available,Seller didnt add any Products yet, comeback later")
        else:
            user.customer_flow(user, product_list)
    else:
        print("Invalid Role!!!!")


if __name__ == "__main__":
    main()
