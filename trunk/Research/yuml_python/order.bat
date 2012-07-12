del order.png
python create_yuml_class_diagram.py "[Customer]+1->*[Order], [Order]++1-items>*[LineItem], [Order]-0..1>[PaymentMethod], [Andy]>[Python]" yuml_order_example.png
