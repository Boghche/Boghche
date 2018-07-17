import math

from flask import (request, render_template, redirect, url_for,
	jsonify, abort)
from flask_login import login_required

from fardel.ext import db
from ..panel import mod
from .models import *
from ....core.auth.models import User

from fardel.core.panel.decorator import staff_required

@staff_required
@mod.route('/orders/list/')
@login_required
def orders_list():
	page = request.args.get('page', default=1, type=int)
	per_page = request.args.get('per_page', default=20, type=int)
	query = Order.query.order_by(Order.create_time.asc())
	pages = math.ceil(query.count() / per_page)
	orders = query.paginate(page=page, per_page=per_page, error_out=False).items
	return render_template('order/orders_list.html',
		orders=orders)

@staff_required
@mod.route('/orders/list/<int:order_id>')
@login_required
def orders_info(order_id):
	order = Order.query.filter_by(id=order_id).first_or_404()
	user = User.query.filter_by(id=order.user_id).first_or_404()
	print(order.lines)
	return render_template('order/orders_info.html', order=order, user=user)

@staff_required
@mod.route('/orders/confirm_order/<int:order_id>')
@login_required    
def confirm_order(order_id):
	order = Order.query.filter_by(id=order_id).first_or_404()
	if order.status == "Unfulfiled":
		order.status = "Fulfiled"
	elif order.status == "Fulfiled"	:
		order.status = "Unfulfiled"
	db.session.commit()	
	return redirect(url_for('ecommerce_panel.orders_list'))

@staff_required
@mod.route('/orders/delete/<int:order_id>')
@login_required    
def order_delete(order_id):
	order = Order.query.filter_by(id=order_id).first_or_404()
	db.session.delete(order)
	db.session.commit()
	return redirect(url_for('ecommerce_panel.orders_list'))
