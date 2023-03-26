class InventoryItem:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.category = kwargs.get('category')
        self.price = float(kwargs.get('price'))
