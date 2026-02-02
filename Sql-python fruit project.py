import mysql.connector

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",          # change if needed
    password="Sree@189",
    database="sree"
)
cursor = db.cursor()

# ---------------- MAIN MENU ----------------
while True:
    print("\n======> LOGIN INFO <======")
    print("1. Customer")
    print("2. Shopkeeper")
    print("3. Exit")

    ch = input("Choose one option: ")

    if not ch.isdigit():
        print("Invalid input")
        continue

    ch = int(ch)

    # ---------------- CUSTOMER LOGIN ----------------
    if ch == 1:
        name = input("Enter your name: ")

        while True:
            mobile = input("Enter mobile number: ")
            if mobile.isdigit() and len(mobile) == 10 and mobile[0] in "6789":
                mobile = int(mobile)
                break
            else:
                print("Invalid mobile number")
        

        # insert customer
        cursor.execute(
            "INSERT INTO customers (name, mobile) VALUES (%s, %s)",
            (name, mobile)
        )
        db.commit()
        customer_id = cursor.lastrowid

        # create cart
        cursor.execute(
            "INSERT INTO cart (customer_id) VALUES (%s)",
            (customer_id,)
        )
        db.commit()
        cart_id = cursor.lastrowid
       # check if customer already exists
        '''cursor.execute(
            "SELECT customer_id, name FROM customers WHERE mobile = %s",
            (mobile,)
        )
        customer = cursor.fetchone()

        if customer:
            customer_id = customer[0]
            print("Welcome back,", customer[1])
        else:
            cursor.execute(
                "INSERT INTO customers (name, mobile) VALUES (%s, %s)",
                (name, mobile)
            )
            db.commit()
            customer_id = cursor.lastrowid
            print("New customer registered")'''
        # ---------------- CUSTOMER PANEL ----------------
        while True:
            print("\n======> CUSTOMER PANEL <======")
            print("1. Add Item to Cart")
            print("2. Remove Item from Cart")
            print("3. View Cart")
            print("4. Display Menu")
            print("5. Exit & Bill")

            op = input("Choose option: ")

            if not op.isdigit():
                print("Invalid input")
                continue

            op = int(op)

            # -------- ADD ITEM --------
            if op == 1:
                frt = input("Which fruit do you want: ").lower()

                # 1. Check if fruit exists
                cursor.execute(
                    "SELECT fruit_id, quantity FROM fruits_shop WHERE fruit_name = %s",
                    (frt,)
                )
                fruits_shop = cursor.fetchone()

                if not fruits_shop:
                    print("Out of stock")
                else:
                    fruit_id, stock_qty = fruits_shop

                    # 2. Check if fruit already in cart
                    cursor.execute(
                        "SELECT quantity FROM cart_items WHERE cart_id = %s AND fruit_id = %s",
                        (cart_id, fruit_id)
                    )
                    cart_data = cursor.fetchone()

                    # ---------------- ALREADY IN CART ----------------
                    if cart_data:
                        print(f"{frt} is already in your cart")
                        print("1.Yes\n2.No")
                        op = input("Do you want to add more? ")

                        if op.isdigit() and int(op) == 1:
                            quant = int(input("Enter quantity to add: "))

                            if quant > 0 and stock_qty >= quant:

                                # update cart quantity
                                cursor.execute(
                                    "UPDATE cart_items SET quantity = quantity + %s "
                                    "WHERE cart_id = %s AND fruit_id = %s",
                                    (quant, cart_id, fruit_id)
                                )

                                # reduce stock
                                cursor.execute(
                                    "UPDATE fruits_shop SET quantity = quantity - %s "
                                    "WHERE fruit_id = %s",
                                    (quant, fruit_id)
                                )

                                db.commit()
                                print("Quantity updated in cart")

                            else:
                                print("Only", stock_qty, "kgs available")

                    # ---------------- NOT IN CART ----------------
                    else:
                        quant = int(input("How much quantity do you want to add: "))

                        if quant > 0 and stock_qty >= quant:

                            # insert into cart
                            cursor.execute(
                                "INSERT INTO cart_items (cart_id, fruit_id, quantity) "
                                "VALUES (%s, %s, %s)",
                                (cart_id, fruit_id, quant)
                            )

                            # reduce stock
                            cursor.execute(
                                "UPDATE fruits_shop SET quantity = quantity - %s "
                                "WHERE fruit_id = %s",
                                (quant, fruit_id)
                            )

                            db.commit()
                            print("Item added to cart")

                        else:
                            print("Only", stock_qty, "kgs available")

            #---------REMOVE ITEM--------
            elif op == 2:
                frt = input("Which fruit do you want to remove: ").lower()

                # get fruit_id
                cursor.execute(
                    "SELECT fruit_id FROM fruits_shop WHERE fruit_name = %s",
                    (frt,)
                )
                fruits_shop = cursor.fetchone()

                if not fruits_shop:
                    print(frt, "not found")
                else:
                    fruit_id = fruits_shop[0]

                    # check if fruit is in cart
                    cursor.execute(
                        "SELECT quantity FROM cart_items WHERE cart_id = %s AND fruit_id = %s",
                        (cart_id, fruit_id)
                    )
                    cart_data = cursor.fetchone()

                    if not cart_data:
                        print(frt, "not in your cart")
                    else:
                        cart_qty = cart_data[0]
                        quant = int(input("How much quantity do you want to remove: "))

                        if quant > 0 and quant <= cart_qty:

                            # return quantity to stock
                            cursor.execute(
                                "UPDATE fruits_shop SET quantity = quantity + %s WHERE fruit_id = %s",
                                (quant, fruit_id)
                            )

                            remaining_qty = cart_qty - quant

                            # if quantity becomes zero → delete item
                            if remaining_qty == 0:
                                cursor.execute(
                                    "DELETE FROM cart_items WHERE cart_id = %s AND fruit_id = %s",
                                    (cart_id, fruit_id)
                                )
                            else:
                                cursor.execute(
                                    "UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND fruit_id = %s",
                                    (remaining_qty, cart_id, fruit_id)
                                )

                            db.commit()
                            print("Item removed successfully")

                        else:
                            print("Invalid quantity")

            # -------- VIEW CART --------
            elif op == 3:
                cursor.execute("""
                SELECT f.fruit_name, c.quantity, f.selling_price,
                       c.quantity * f.selling_price AS total
                FROM cart_items c
                JOIN fruits_shop f ON c.fruit_id = f.fruit_id
                WHERE c.cart_id = %s
                """, (cart_id,))

                cart_items = cursor.fetchall()

                if not cart_items:
                    print("Cart is empty")
                else:
                    total = 0
                    print("\n----- CART -----")
                    for i in cart_items:
                        print(i[0], "-", i[1], "kg - Rs.", i[3])
                        total += i[3]
                    print("Total Amount:", total)

            #---------DISPLAY MENU-------
            elif op == 4:
                cursor.execute(
                    "SELECT fruit_id, fruit_name, quantity, selling_price FROM fruits_shop"
                )
                fruits_shop = cursor.fetchall()

                print("\n------ MENU ------")
                for f in fruits_shop:
                    print(f"ID:{f[0]}  {f[1]} - {f[2]} kg - Rs.{f[3]}")
                print("------------------")

            # -------- EXIT & BILL --------
            elif op == 5:
                cursor.execute("""
                SELECT SUM(c.quantity * f.selling_price)
                FROM cart_items c
                JOIN fruits_shop f ON c.fruit_id = f.fruit_id
                WHERE c.cart_id = %s
                """, (cart_id,))

                total = cursor.fetchone()[0]
                total = total if total else 0

                print("\n------ BILL ------")
                print("Name   :", name)
                print("Mobile :", mobile)
                print("Total  : Rs.", total)
                print("Thank you for shopping!")
                break

            else:
                print("Invalid option")

    #-------------SHOPKEEPER LOGIN------------#
    elif ch == 2:
        while True:
            print("======= SHOPKEEPER PANEL ======")
            print("1. Add items to stock")
            print("2. Remove items from stock")
            print("3. Modify cost")
            print("4. View stock")
            print("5. check item")
            print("6. Profit")
            print("7. Exit")

            op = input("Enter option: ")

            if not op.isdigit():
                print("Invalid Option")
                continue

            op = int(op)

            #-----------ADD ITEMS----------
            if op == 1:
                frt = input("Fruit name: ").lower()
                quant = int(input("Quantity to add: "))
                cp = int(input("Cost price per kg: "))
                sp = int(input("Selling price per kg: "))

                cursor.execute(
                    "SELECT fruit_id FROM fruits_shop WHERE fruit_name = %s",
                    (frt,)
                )
                row = cursor.fetchone()

                if row:
                    cursor.execute(
                        "UPDATE fruits_shop SET quantity = quantity + %s WHERE fruit_name = %s",
                        (quant, frt)
                    )
                    print("Quantity updated")
                else:
                    cursor.execute(
                        "INSERT INTO fruits_shop (fruit_name, quantity, cost_price, selling_price) "
                        "VALUES (%s, %s, %s, %s)",
                        (frt, quant, cp, sp)
                    )
                    print("New fruit added")

                db.commit()
            #------------REMOVE ITEM---------
            elif op == 2:
                frt = input("Remove fruit: ").lower()
                quant = int(input("Quantity to remove: "))

                cursor.execute(
                    "SELECT quantity FROM fruits_shop WHERE fruit_name = %s",
                    (frt,)
                )
                row = cursor.fetchone()

                if row:
                    if row[0] > quant:
                        cursor.execute(
                            "UPDATE fruits_shop SET quantity = quantity - %s WHERE fruit_name = %s",
                            (quant, frt)
                        )
                        print("Quantity reduced")
                    elif row[0] == quant:
                        cursor.execute(
                            "DELETE FROM fruits_shop WHERE fruit_name = %s",
                            (frt,)
                        )
                        print("Fruit removed completely")
                    else:
                        print("Not enough stock")
                    db.commit()
                else:
                    print("Fruit not found")
            #-----------MODIFY COST/SELLING PRICE-------
            elif op == 3:
                frt = input("Fruit name: ").lower()

                print("1. Increase\n2. Decrease")
                ch = int(input("Choose option: "))

                print("1. Cost Price\n2. Selling Price")
                x = int(input("Choose option: "))

                amt = int(input("Amount: "))

                column = "cost_price" if x == 1 else "selling_price"
                sign = "+" if ch == 1 else "-"

                cursor.execute(
                    f"UPDATE fruits_shop SET {column} = {column} {sign} %s WHERE fruit_name = %s",
                    (amt, frt)
                )

                db.commit()
                print("Price updated")
            #-----------VIEW STOCK-----------
            elif op == 4:
                cursor.execute("SELECT fruit_name, quantity, selling_price, cost_price FROM fruits_shop")
                rows = cursor.fetchall()

                for r in rows:
                    print(r[0], r[1], "kg", "SP:", r[2], "CP:", r[3])
            #------------CHECK ITEM-----------
            elif op == 5:
                frt = input("Fruit name: ").lower()

                cursor.execute(
                    "SELECT 1 FROM fruits_shop WHERE fruit_name = %s",
                    (frt,)
                )

                print("Available" if cursor.fetchone() else "Not available")
            #--------------PROFIT (Simple Version)----------
            elif op == 6:
                cursor.execute(
                    "SELECT SUM((selling_price - cost_price) * quantity) FROM fruits_shop"
                )
                profit = cursor.fetchone()[0]

                if profit:
                    print("Profit:", profit)
                else:
                    print("No profit yet")
            #----------------EXIT----------
            elif op == 7:
                break
            else:
                print("Invalid Option")

    elif ch == 3:
        print("Thank You!")
        print("----Visit Again----")
        break
    else:
        print("Invalid Input")

    




























        
