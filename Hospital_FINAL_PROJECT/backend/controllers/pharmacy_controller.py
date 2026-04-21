from flask import request, redirect, render_template, flash, session
from backend.models.pharmacy_model import (
    add_medicine,
    get_all_medicines,
    get_medicine_by_id,
    update_medicine,
    delete_medicine,
    is_stock_available,
    decrement_stock,
    create_sale,
    add_sale_item,
    get_sales,
    get_sales_by_patient,
    get_sale_items,
    create_prescription,
    add_prescription_item,
    get_prescriptions_by_doctor,
    get_prescriptions_by_patient,
    get_prescription_items,
    init_pharmacy_tables,
)
from backend.models.patient_model import get_all_patients, get_patient_by_user_id
from backend.models.doctor_model import get_doctor_by_user_id
from backend.models.billing_model import init_billing_tables, create_bill, add_bill_item, update_bill_status
from backend.utils.auth import get_current_user_id, get_current_user_role
from datetime import datetime


def pharmacy_redirect():
    role = get_current_user_role()
    if role == 'admin':
        return redirect('/admin/medicines')
    if role == 'doctor':
        return redirect('/doctor/prescription')
    if role == 'patient':
        return redirect('/my-prescriptions')
    return redirect('/dashboard')


def admin_medicines():
    medicines = get_all_medicines()
    low_stock = [m for m in medicines if m[3] <= 5]
    return render_template('admin_medicines.html', medicines=medicines, low_stock=low_stock)


def admin_add_medicine():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')
        expiry_date = request.form.get('expiry_date')

        if not name or not price or not stock:
            flash('Medicine name, price, and stock are required.', 'danger')
            return redirect('/admin/add-medicine')

        add_medicine(name.strip(), float(price), int(stock), expiry_date or None)
        flash('Medicine added successfully.', 'success')
        return redirect('/admin/medicines')

    return render_template('add_edit_medicine.html', medicine=None, action='Add')


def admin_edit_medicine(medicine_id):
    medicine = get_medicine_by_id(medicine_id)
    if not medicine:
        flash('Medicine not found.', 'danger')
        return redirect('/admin/medicines')

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')
        expiry_date = request.form.get('expiry_date')

        if not name or not price or not stock:
            flash('Medicine name, price, and stock are required.', 'danger')
            return redirect(f'/admin/edit-medicine/{medicine_id}')

        update_medicine(
            medicine_id,
            name.strip(),
            float(price),
            int(stock),
            expiry_date or None,
        )
        flash('Medicine updated successfully.', 'success')
        return redirect('/admin/medicines')

    return render_template('add_edit_medicine.html', medicine=medicine, action='Edit')


def admin_delete_medicine(medicine_id):
    delete_medicine(medicine_id)
    flash('Medicine deleted successfully.', 'success')
    return redirect('/admin/medicines')


def admin_sell_medicine():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')

        if not patient_id:
            flash('Please select a patient.', 'danger')
            return redirect('/admin/sell-medicine')

        cart = []
        total_amount = 0.0
        for medicine_id, quantity in zip(medicine_ids, quantities):
            if not medicine_id or not quantity:
                continue

            quantity = int(quantity)
            medicine = get_medicine_by_id(int(medicine_id))
            if not medicine:
                continue

            if quantity <= 0:
                flash('Quantity must be greater than zero.', 'danger')
                return redirect('/admin/sell-medicine')

            if not is_stock_available(int(medicine_id), quantity):
                flash(f"Insufficient stock for {medicine[1]}.", 'danger')
                return redirect('/admin/sell-medicine')

            subtotal = medicine[2] * quantity
            cart.append({
                'medicine_id': int(medicine_id),
                'name': medicine[1],
                'price': medicine[2],
                'quantity': quantity,
                'subtotal': subtotal,
            })
            total_amount += subtotal

        if not cart:
            flash('Add at least one medicine to the cart.', 'danger')
            return redirect('/admin/sell-medicine')

        sale_id = create_sale(int(patient_id), total_amount)
        for item in cart:
            add_sale_item(sale_id, item['medicine_id'], item['quantity'], item['price'])
            decrement_stock(item['medicine_id'], item['quantity'])

        # integrate with billing module
        try:
            init_billing_tables()
            bill_id = create_bill(int(patient_id))
            for item in cart:
                add_bill_item(
                    bill_id,
                    f"{item['name']} x{item['quantity']}",
                    item['subtotal'],
                )
            update_bill_status(bill_id, 'Paid')
        except Exception:
            pass

        flash('Sale completed and stock updated successfully.', 'success')
        return redirect('/admin/sales')

    patients = get_all_patients()
    medicines = get_all_medicines()
    return render_template('sell_medicine.html', patients=patients, medicines=medicines)


def admin_sales_history():
    sales = get_sales()
    outlined_sales = []
    for sale in sales:
        outlined_sales.append({
            'id': sale[0],
            'patient_id': sale[1],
            'patient_name': sale[2],
            'total_amount': sale[3],
            'date': sale[4],
            'items': get_sale_items(sale[0]),
        })
    return render_template('sales_history.html', sales=outlined_sales)


def doctor_prescriptions():
    doctor = get_doctor_by_user_id(get_current_user_id())
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect('/dashboard')

    prescriptions = get_prescriptions_by_doctor(doctor[0])
    prescription_rows = []
    for prescription in prescriptions:
        items = get_prescription_items(prescription[0])
        prescription_rows.append({
            'id': prescription[0],
            'patient_name': prescription[2],
            'notes': prescription[3],
            'date': prescription[4],
            'items': items,
        })
    return render_template('doctor_prescriptions.html', prescriptions=prescription_rows)


def doctor_add_prescription():
    doctor = get_doctor_by_user_id(get_current_user_id())
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect('/dashboard')

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        notes = request.form.get('notes')
        medicine_ids = request.form.getlist('medicine_id[]')
        dosages = request.form.getlist('dosage[]')
        durations = request.form.getlist('duration[]')

        if not patient_id:
            flash('Please select a patient.', 'danger')
            return redirect('/doctor/add-prescription')

        if not medicine_ids:
            flash('Add at least one medicine to the prescription.', 'danger')
            return redirect('/doctor/add-prescription')

        prescription_id = create_prescription(int(patient_id), doctor[0], notes)
        for medicine_id, dosage, duration in zip(medicine_ids, dosages, durations):
            if not medicine_id or not dosage or not duration:
                continue
            add_prescription_item(prescription_id, int(medicine_id), dosage, duration)

        flash('Prescription created successfully.', 'success')
        return redirect('/doctor/prescription')

    patients = get_all_patients()
    medicines = get_all_medicines()
    return render_template('doctor_add_prescription.html', patients=patients, medicines=medicines)


def patient_prescriptions():
    patient = get_patient_by_user_id(get_current_user_id())
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect('/dashboard')

    prescriptions = get_prescriptions_by_patient(patient[0])
    prescription_rows = []
    for prescription in prescriptions:
        items = get_prescription_items(prescription[0])
        prescription_rows.append({
            'id': prescription[0],
            'doctor_name': prescription[2],
            'notes': prescription[3],
            'date': prescription[4],
            'items': items,
        })
    return render_template('patient_prescriptions.html', prescriptions=prescription_rows)


def patient_purchases():
    patient = get_patient_by_user_id(get_current_user_id())
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect('/dashboard')

    sales = get_sales_by_patient(patient[0])
    purchases = []
    for sale in sales:
        items = get_sale_items(sale[0])
        purchases.append({
            'id': sale[0],
            'total_amount': sale[1],
            'date': sale[2],
            'items': items,
        })
    return render_template('patient_purchases.html', purchases=purchases)