from products.models import Product,ProductVariant,Attribute,AttributeValue,VariantAttributeValue
from django.db.models import Prefetch

class ProcessProductInput:
    def __init__(self):
        pass

    def process_input_product(self,product_data,deletion_data):

        delete_product_id = deletion_data.get('product_id',None)

        if delete_product_id:
            return delete_product_id,True
        
        product_id = product_data.get('id',None)
        return product_id,False
    
    def process_input_variants(self,variants,deletion_data):

        update_variants = []
        create_variants = []

        for variant in variants:
            variant_id = variant.get('id',None)
            
            if variant_id:
                update_variants.append(variant)
            else:
                create_variants.append(variant)
        
        return create_variants,update_variants
            


        
