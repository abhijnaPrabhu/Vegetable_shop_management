from nicegui import ui,app

from database import (
    add_vegetable,
    get_vegetables,
    update_vegetable,
    set_vegetable_active,
    set_daily_stock,
    get_today_stock,
    get_available_vegetables_today,
    place_order,
    get_orders,
    get_order_items,
    update_order_status,
    get_order_history
)


@ui.page('/')
def home():
    ui.navigate.to('/admin')


@ui.page('/admin')
def admin_page():

    with ui.column().classes(
        'w-full min-h-screen bg-green-50'
    ):

        # ---------------- HEADER ----------------

        with ui.row().classes(
            'w-full items-center justify-between px-10 py-4 bg-white shadow-sm'
        ):

            ui.label(
                'VeggieMart Admin'
            ).classes(
                'text-2xl font-bold text-green-700'
            )

            ui.button(
                'View Orders',
                on_click=lambda:ui.navigate.to('/admin/orders'),
                icon='shopping_cart'
            ).classes('mt-4')

            ui.button(
                'Purchase History',
                on_click=lambda:ui.navigate.to('/admin/history'),
                icon='history'
            ).classes('mt-4')

        # ---------------- MAIN CONTENT ----------------

        with ui.column().classes(
            'w-full items-center px-6 py-10 gap-8'
        ):

            ui.label(
                'Vegetable Management'
            ).classes(
                'text-4xl font-bold text-green-800'
            )

            # ==================================================
            # FUNCTION: CHANGE ACTIVE / INACTIVE STATUS
            # ==================================================

            def change_status(vegetable_id, status):

                set_vegetable_active(
                    vegetable_id,
                    status
                )

                ui.notify(
                    'Vegetable status updated',
                    type='positive'
                )

                vegetable_list.refresh()

            # ==================================================
            # FUNCTION: EDIT VEGETABLE
            # ==================================================

            def open_edit_dialog(vegetable):

                vegetable_id = vegetable[0]
                current_name = vegetable[1]
                current_unit = vegetable[2]

                with ui.dialog() as dialog:

                    with ui.card().classes(
                        'w-96 p-6 rounded-xl'
                    ):

                        ui.label(
                            'Edit Vegetable'
                        ).classes(
                            'text-2xl font-semibold'
                        )

                        edit_name = ui.input(
                            'Vegetable Name',
                            value=current_name
                        ).classes(
                            'w-full'
                        )

                        edit_unit = ui.select(
                            ['kg', 'gram', 'piece', 'bunch'],
                            label='Unit',
                            value=current_unit
                        ).classes(
                            'w-full'
                        )

                        def save_changes():

                            name = edit_name.value
                            unit = edit_unit.value

                            if not name or not unit:

                                ui.notify(
                                    'Name and unit are required',
                                    type='negative'
                                )

                                return

                            try:

                                update_vegetable(
                                    vegetable_id,
                                    name.strip(),
                                    unit
                                )

                                ui.notify(
                                    'Vegetable updated successfully',
                                    type='positive'
                                )

                                dialog.close()

                                vegetable_list.refresh()

                            except Exception as error:

                                ui.notify(
                                    f'Could not update vegetable: {error}',
                                    type='negative'
                                )

                        with ui.row().classes(
                            'w-full justify-end gap-2 mt-4'
                        ):

                            ui.button(
                                'Cancel',
                                on_click=dialog.close
                            ).props(
                                'flat'
                            )

                            ui.button(
                                'Save Changes',
                                on_click=save_changes
                            ).classes(
                                'bg-green-600 text-white'
                            )

                dialog.open()

            # ==================================================
            # ADD VEGETABLE FORM
            # ==================================================

            with ui.card().classes(
                'w-full max-w-lg p-6 rounded-xl shadow-md'
            ):

                ui.label(
                    'Add Vegetable'
                ).classes(
                    'text-2xl font-semibold'
                )

                name_input = ui.input(
                    'Vegetable Name'
                ).classes(
                    'w-full'
                )

                unit_input = ui.select(
                    ['kg', 'gram', 'piece', 'bunch'],
                    label='Unit'
                ).classes(
                    'w-full'
                )

                def save_vegetable():

                    name = name_input.value
                    unit = unit_input.value

                    if not name or not unit:

                        ui.notify(
                            'Please enter vegetable name and unit',
                            type='negative'
                        )

                        return

                    try:

                        add_vegetable(
                            name.strip(),
                            unit
                        )

                        ui.notify(
                            'Vegetable added successfully',
                            type='positive'
                        )

                        name_input.value = ''
                        unit_input.value = None

                        vegetable_list.refresh()

                    except Exception as error:

                        ui.notify(
                            f'Could not add vegetable: {error}',
                            type='negative'
                        )

                ui.button(
                    'Add Vegetable',
                    on_click=save_vegetable
                ).classes(
                    'w-full bg-green-600 text-white mt-4'
                )

            ## ==================================================
            ### VEGETABLE LIST ###
            ## ==================================================

            @ui.refreshable
            def vegetable_list():

                rows = get_vegetables()

                with ui.column().classes(
                    'w-full max-w-2xl gap-3'
                ):

                    ui.label(
                        'Vegetables'
                    ).classes(
                        'text-2xl font-semibold'
                    )

                    if not rows:

                        ui.label(
                            'No vegetables added yet.'
                        ).classes(
                            'text-gray-500'
                        )

                    for vegetable in rows:

                        vegetable_id = vegetable[0]
                        name = vegetable[1]
                        unit = vegetable[2]
                        active = vegetable[3]

                        with ui.card().classes(
                            'w-full p-4 rounded-lg shadow-sm'
                        ):

                            with ui.row().classes(
                                'w-full items-center justify-between'
                            ):

                                # Vegetable information
                                with ui.column().classes(
                                    'gap-1'
                                ):

                                    ui.label(
                                        name
                                    ).classes(
                                        'text-lg font-semibold'
                                    )

                                    ui.label(
                                        f'Unit: {unit}'
                                    ).classes(
                                        'text-gray-500'
                                    )

                                    if active == 1:

                                        ui.label(
                                            'Active'
                                        ).classes(
                                            'text-green-600 font-semibold'
                                        )

                                    else:

                                        ui.label(
                                            'Inactive'
                                        ).classes(
                                            'text-red-500 font-semibold'
                                        )

                                # Buttons
                                with ui.row().classes(
                                    'gap-2 items-center'
                                ):

                                    ui.button(
                                        'Edit',
                                        on_click=lambda v=vegetable:
                                            open_edit_dialog(v)
                                    ).props(
                                        'outline'
                                    )

                                    if active == 1:

                                        ui.button(
                                            'Deactivate',
                                            on_click=lambda vegetable_id=vegetable_id:
                                                change_status(
                                                    vegetable_id,
                                                    0
                                                )
                                        ).props(
                                            'outline color=negative'
                                        )

                                    else:

                                        ui.button(
                                            'Activate',
                                            on_click=lambda vegetable_id=vegetable_id:
                                                change_status(
                                                    vegetable_id,
                                                    1
                                                )
                                        ).props(
                                            'outline color=positive'
                                        )

            vegetable_list()


            @ui.refreshable
            def today_stock_section():

                rows = get_today_stock()

                with ui.column().classes(
                    'w-full max-w-3xl gap-4'
                ):

                    ui.label(
                        "Today's Stock"
                    ).classes(
                        'text-3xl font-bold text-green-800'
                    )

                    ui.label(
                        'Set today\'s price and availability'
                    ).classes(
                        'text-gray-500'
                    )

                    if not rows:

                        ui.label(
                            'No active vegetables available.'
                        ).classes(
                            'text-gray-500'
                        )

                    for row in rows:

                        vegetable_id = row[0]
                        name = row[1]
                        unit = row[2]
                        current_price = row[3]
                        current_available = row[4]

                        with ui.card().classes(
                            'w-full p-5 rounded-xl shadow-sm'
                        ):

                            with ui.row().classes(
                                'w-full items-center justify-between gap-4'
                            ):

                                with ui.column().classes(
                                    'gap-1'
                                ):

                                    ui.label(
                                        name
                                    ).classes(
                                        'text-xl font-semibold'
                                    )

                                    ui.label(
                                        f'Unit: {unit}'
                                    ).classes(
                                        'text-gray-500'
                                    )

                                price_input = ui.number(
                                    label='Today Price',
                                    value=current_price,
                                    min=0,
                                    step=1
                                ).classes(
                                    'w-40'
                                )

                                available_switch = ui.switch(
                                    'Available',
                                    value=current_available == 1
                                )

                                def save_stock(
                                    vegetable_id=vegetable_id,
                                    price_input=price_input,
                                    available_switch=available_switch
                                ):

                                    price = price_input.value

                                    if price is None:

                                        ui.notify(
                                            'Please enter the price',
                                            type='negative'
                                        )

                                        return

                                    available = (
                                        1
                                        if available_switch.value
                                        else 0
                                    )

                                    try:

                                        set_daily_stock(
                                            vegetable_id,
                                            price,
                                            available
                                        )

                                        ui.notify(
                                            'Today\'s stock updated',
                                            type='positive'
                                        )

                                        today_stock_section.refresh()

                                    except Exception as error:

                                        ui.notify(
                                            f'Could not update stock: {error}',
                                            type='negative'
                                        )

                                ui.button(
                                    'Save',
                                    on_click=save_stock
                                ).classes(
                                    'bg-green-600 text-white'
                                )
            today_stock_section()




# Shop Page

@ui.page('/shop')
def shop_page():

    if 'cart' not in app.storage.user:
        app.storage.user['cart']=[]

    with ui.column().classes(
        'w-full min-h-screen bg-green-50'
    ):

        #------Header----

        with ui.row().classes(
            'w-full items-center justify-between px-8 py-4 bg-white shadow-sm'
        ):
            ui.label('VeggieMart').classes(
                'text-3xl fot-bold text-green-700'
            )

            ui.label('Fresh Vegetables, ready for you').classes(
                'text-gray-500'
            )

            ui.button(
                'Cart',
                on_click=lambda:ui.navigate.to('/cart').classes(
                    'bg-green-600 text-white'
                )
            )

        #------Main Content-------


        with ui.column().classes(
            'w-full items-center px-6 py-10 gap-6'
        ):

            ui.label("Today's Vegetables").classes(
                'text-4xl font-bold text-green-800'
            )

            ui.label('Choose from vegetables available today').classes(
                'text-gray-500 text-lg'
            )

            vegetables=get_available_vegetables_today()

            if not vegetables:

                ui.label('No vegetables right now').classes(
                    'text-gray-500 text-lg mt-8'
                )

            else:

                with ui.row().classes(
                    'w-full max-w-5xl gap-5 justify-center'
                ):
                    for vegetable in vegetables:

                        stock_id=vegetable[0]
                        vegetable_id=vegetable[1]
                        name=vegetable[2]
                        unit=vegetable[3]
                        price=vegetable[4]

                        def add_to_cart(
                                stock_id=stock_id,
                                vegetable_id=vegetable_id,
                                name=name,
                                unit=unit,
                                price=price
                        ):

                            cart=app.storage.user['cart']

                            already_added=any(
                                item['vegetable_id']==vegetable_id
                                for item in cart
                            )

                            if already_added:
                                ui.notify(
                                    f'{name} is already in your cart',
                                    type='warning'
                                )
                                return

                            cart.append({
                                'stock_id':stock_id,
                                'vegetable_id':vegetable_id,
                                'name':name,
                                'unit':unit,
                                'price':price,
                                'quantity':1,
                                'selected_unit':unit
                            })

                            app.storage.user['cart']=cart

                            ui.notify(
                                f'{name} added to cart',
                                type='positive'
                            )



                        with ui.card().classes(
                            'w-64 p-5 rounded-xl shadow-md'
                        ):
                            ui.label(name).classes(
                                'text-2xl font-semibold text-green-800'
                            )
                            ui.label(f'{price} per {unit}').classes(
                                'text-lg font-medium'
                            )

                            ui.label('Available today').classes(
                                'text-green-600 font-semibold'
                            )

                        ui.button(
                            'Add to Cart',
                            on_click=add_to_cart
                        ).classes(
                            'w-full p-5 bg-green-600 text-white mt-4'
                        )




@ui.page('/cart')
def cart_page():

    cart = app.storage.user.get('cart', [])

    def save_cart_quantity(vegetable_id,quantity,selected_unit):

        cart=app.storage.user.get('cart',[])

        for item in cart:
            if item['vegetable_id']==vegetable_id:
                item['quantity']=quantity
                item['selected_unit']=selected_unit
                break

        app.storage.user['cart']=cart

    def remove_from_cart(vegetable_id):

        cart=app.storage.user.get('cart',[])

        updated_cart=[
            item for item in cart
            if item['vegetable_id']!=vegetable_id
        ]

        app.storage.user['cart']=updated_cart

        ui.notify('Vegetable removed from the cart',
                  type='positive')

        ui.navigate.to('/cart')

    with ui.column().classes(
        'w-full min-h-screen bg-green-50'
    ):

        # ---------- HEADER ----------

        with ui.row().classes(
            'w-full items-center justify-between px-8 py-4 bg-white shadow-sm'
        ):
            ui.label('Your Cart').classes(
                'text-3xl font-bold text-green-700'
            )

            ui.button(
                'Back to Shop',
                on_click=lambda: ui.navigate.to('/shop')
            ).props('outline')

        # ---------- CART CONTENT ----------

        with ui.column().classes(
            'w-full items-center px-6 py-10 gap-5'
        ):

            ui.label('Your Selected Vegetables').classes(
                'text-3xl font-bold text-green-800'
            )

            if not cart:
                ui.label('Your cart is empty').classes(
                    'text-gray-500 text-lg'
                )

            else:

                item_totals = {}
                grand_total_label = None

                def update_grand_total():
                    total = sum(item_totals.values())

                    if grand_total_label is not None:
                        grand_total_label.set_text(
                            f'Grand Total: ₹{total:.2f}'
                        )

                with ui.column().classes(
                    'w-full max-w-2xl gap-3'
                ):

                    for item in cart:

                        vegetable_id = item['vegetable_id']
                        price = item['price']

                        saved_quantity=item.get('quantity',1)
                        saved_unit=item.get('selected_unit',item['unit'])

                        if item['unit']=='kg' and saved_unit=='grams':
                            initial_total=(saved_quantity or 0) /1000 * price
                        else:
                            initial_total=(saved_quantity or 0)*price

                        item_totals[vegetable_id]=initial_total

                        with ui.card().classes(
                            'w-full p-5 rounded-xl shadow-sm gap-4'
                        ):

                            # ---------- NAME AND PRICE ----------

                            with ui.row().classes(
                                'w-full items-center justify-between'
                            ):
                                ui.label(item['name']).classes(
                                    'text-xl font-semibold text-green-700'
                                )

                                ui.label(
                                    f"₹{price:.2f} per {item['unit']}"
                                ).classes(
                                    'text-lg text-gray-700'
                                )

                            # ---------- QUANTITY ----------

                            if item['unit'] == 'kg':

                                with ui.row().classes(
                                    'w-full items-center gap-4'
                                ):

                                    quantity = ui.number(
                                        'Quantity',
                                        value=item.get('quantity',1),
                                        min=500 if item.get('selected_unit','kg')=='grams' else 1
                                    ).classes('w-40')

                                    quantity_unit = ui.select(
                                        ['kg', 'grams'],
                                        value=item.get('selected_unit','kg'),
                                        label='Unit'
                                    ).classes('w-40')

                            else:

                                quantity = ui.number(
                                    f"Quantity ({item['unit']})",
                                    value=item.get('quantity',1),
                                    min=1,
                                    step=1,
                                    precision=0
                                ).classes('w-40')

                                quantity_unit = None

                            #---------Remove button-------

                            ui.button(
                                'Remove',
                                icon='delete',
                                on_click=lambda vegetable_id=vegetable_id:
                                remove_from_cart(vegetable_id)
                            ).props(
                                'outline color=negative'
                            ).classes(
                                'self-end'
                            )

                            # ---------- ITEM TOTAL ----------

                            item_total = ui.label(
                                f'Item Total: ₹{price:.2f}'
                            ).classes(
                                'text-lg font-semibold text-green-700'
                            )

                            # ---------- CALCULATION ----------

                            def calculate_total(
                                quantity=quantity,
                                quantity_unit=quantity_unit,
                                price=price,
                                vegetable_id=vegetable_id,
                                item_total=item_total,
                                base_unit=item['unit']
                            ):

                                value = quantity.value

                                if value is None:
                                    total = 0

                                elif base_unit == 'kg':

                                    if quantity_unit.value == 'grams':
                                        minimum = 500
                                        quantity_in_kg = value / 1000
                                    else:
                                        minimum = 1
                                        quantity_in_kg = value

                                    total = (
                                        quantity_in_kg * price
                                        if value >= minimum else 0
                                    )

                                else:

                                    total = (
                                        value * price
                                        if value >= 1
                                        and float(value).is_integer()
                                        else 0
                                    )

                                item_totals[vegetable_id] = total

                                save_cart_quantity(
                                    vegetable_id,
                                    quantity.value,
                                    quantity_unit.value if quantity_unit is not None else base_unit
                                )

                                item_total.set_text(
                                    f'Item Total: ₹{total:.2f}'
                                )

                                update_grand_total()

                            # ---------- EVENTS ----------

                            quantity.on(
                                'update:model-value',
                                lambda e, fn=calculate_total: fn()
                            )

                            if quantity_unit is not None:

                                def change_unit(
                                    quantity=quantity,
                                    quantity_unit=quantity_unit
                                ):

                                    if quantity_unit.value == 'grams':
                                        quantity.props('min=500')
                                        quantity.value = 500
                                    else:
                                        quantity.props('min=1')
                                        quantity.value = 1

                                quantity_unit.on(
                                    'update:model-value',
                                    lambda e, fn=change_unit: fn()
                                )

                                quantity_unit.on(
                                    'update:model-value',
                                    lambda e, fn=calculate_total: fn()
                                )

                    # ---------- GRAND TOTAL ----------
                    # Outside the vegetable loop

                    with ui.card().classes(
                        'w-full p-5 rounded-xl shadow-sm bg-green-100'
                    ):

                        grand_total_label = ui.label(
                            f"Grand Total: ₹{sum(item_totals.values()):.2f}"
                        ).classes(
                            'text-2xl font-bold text-green-800'
                        )


                    #------------PLACE ORDER FUNCTION--------
                    with ui.card().classes('w-full max-w-lg mt-4'):
                        ui.label('Checkout').classes('text-xl font-bold')

                        customer_name=ui.input(
                            label='Your name',
                            placeholder='Enter your name'
                        ).classes('w-full')

                        def submit_order():
                            name=(customer_name.value or '').strip()

                            if not name:
                                ui.notify('Please enter your name',type='warning')
                                return

                            cart=app.storage.user.get('cart',[])

                            if not cart:
                                ui.notify('Your cart is empty',type='warning')
                                return

                            try:
                                print("Cart data: ",cart)
                                order_id=place_order(name,cart)
                                print('Order saved sucessfully!',order_id)
                                

                            except ValueError as error:
                                ui.notify(
                                    str(error),
                                    type='negative'
                                )
                                return

                            except Exception as error:
                                print('Database/Unexpected error',repr(error))
                                ui.notify('Unable to place order. Please try again',type='negative')
                                return

                            app.storage.user['cart']=[]

                            ui.notify(
                                f'Order #{order_id} placed successfully!',
                                type='positive'
                            )

                            ui.navigate.to('/shop')

                        ui.button(
                            'Place order',
                            on_click=submit_order,
                            color='positive'
                        ).classes('w-full')





@ui.page('/admin/orders')
def admin_orders():

    ui.label('Incoming Orders').classes('text-2xl font-bold')

    ui.button('Back to Admin',on_click=lambda:ui.navigate.to('/admin'),icon='arrow_back')

    orders=get_orders()

    if not orders:
        ui.label('No pending orders').classes(
            'text-gray-500 mt-4'
        )
        return

    for order in orders:
        order_id,customer_name,order_date,total,status=order

        with ui.card().classes('w-full max-w-lg mt-4'):
            ui.label(f'Order #{order_id}').classes('text-lg font-bold')
            ui.label(f'Customer: {customer_name}')
            ui.label(f'Date: {order_date}')
            ui.label(f'Total: ₹{total:.2f}')
            ui.label(f'Status: {status}')

            ui.separator()

            ui.label('Ordered Vegetables').classes(
                'text-md font-semibold mt-2'
            )

            items=get_order_items(order_id)

            if not items:
                ui.label('No items found').classes('text-gray-500')

            else:
                for item in items:
                    vegetable_name,quantity,unit,price,subtotal=item

                    with ui.row().classes(
                        'w-full justify-between items-center'
                    ):
                        ui.label(
                            f'{vegetable_name}-{quantity:g}{unit}'
                        )
                        ui.label(
                            f'₹{subtotal:.2f}'
                        )


            ui.separator()

            def change_status(new_status,selected_order_id=order_id):
                try:
                    update_order_status(selected_order_id,new_status)

                    ui.notify(
                        f'Order #{selected_order_id} marked as {new_status}',type='positive'
                    )

                    ui.navigate.to('/admin/orders')

                except ValueError as error:
                    ui.notify(str(error),type='negative')

                except Exception as error:
                    ui.notify(
                        'Unable to update order status',
                        type='negative'
                    )

            if status=='Pending':
                ui.button(
                    'Start Preparing',
                    on_click=lambda:change_status('Preparing'),
                    color='primary'
                )

            elif status=='Preparing':
                ui.button(
                    'Mark Completed',
                    on_click=lambda:change_status('Completed'),
                    color='positive'
                )



@ui.page('/admin/history')
def admin_history():

    ui.label('Purchase History').classes(
        'text-2xl font-bold'
    )

    ui.button('Back to Admin',
              on_click=lambda:ui.navigate.to('/admin'))

    orders=get_order_history()

    if not orders:
        ui.label('No order history available')
        return

    for order in orders:
        order_id,customer_name,order_date,total,status=order

        with ui.card().classes('w-full max-w-lg mt-4'):

            ui.label(f'Order #{order_id}').classes(
                'text-lg font-bold'
            )

            ui.label(f'Customer: {customer_name}')
            ui.label(f'Date: {order_date}')
            ui.label(f'Total: ₹{total:.2f} ').classes(
                'font-bold'
            )

            ui.separator()

            items=get_order_items(order_id)

            for item in items:
                vegetable_name,quantity,unit,price,subtotal=item

                with ui.row().classes('w-full justify-between'):
                    ui.label(f'{vegetable_name}-{quantity:g}{unit}')
                    ui.label(f'₹{subtotal:.2f}')





ui.run(
    storage_secret='vegetable-shop-secret'
)
