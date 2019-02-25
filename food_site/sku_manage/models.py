import re

from django.db import models
from django.core.exceptions import ValidationError

weights = ('Ounce', 'oz.', 'Pound', 'lb.', 'Ton', 'ton.', 'Gram', 'g.', 'Kilogram', 'kg.')
volumes = ('Fluid Ounce', 'fl.oz.', 'Pint', 'pt.', 'Quart', 'qt.', 'Gallon', 'gal.', 'Milliliter', 'mL', 'Liter', 'L')
counts = ('Count', 'count',)

def validate_upc(value):
    if len(value) != 12:
        raise ValidationError('UPC must be 12 digits long')
    pattern = re.compile('[0-9]{12}')
    if pattern.match(value) is None:
        raise ValidationError('UPC must only contain numbers')
    if 0 < int(value[0]) < 6:
        raise ValidationError('UPC first digit is not valid')
    sum_val = 0
    for i in range(0, 6):
        sum_val += int(value[i * 2])
    sum_val = sum_val * 3
    for i in range(0, 6):
        sum_val += int(value[i * 2 + 1])
    if sum_val % 10 != 0:
        raise ValidationError('UPC check digit is not valid')


def validate_gt_zero(value):
    if value <= 0:
        raise ValidationError('Must be greater than zero')


def gen_ingr_num():
    ingredients = Ingredient.objects.order_by('number')
    if len(ingredients) > 0 and ingredients[len(ingredients) - 1].number > len(ingredients) - 1:
        for i in range(0, len(ingredients)):
            if (ingredients[i].number > i):
                return i
    return len(ingredients)


def gen_sku_num():
    skus = SKU.objects.order_by('sku_num')
    if len(skus) > 0 and skus[len(skus) - 1].sku_num > len(skus) - 1:
        for i in range(0, len(skus)):
            if (skus[i].sku_num > i):
                return i
    return len(skus)


def gen_fla_num():
    formulas = Formula.objects.order_by('number')
    if len(formulas) > 0 and formulas[len(formulas) - 1].number > len(formulas) - 1:
        for i in range(0, len(formulas)):
            if (formulas[i].number > i):
                return i
    return len(formulas)


class Ingredient(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name='Ingredient Name')
    number = models.PositiveIntegerField(unique=True, default=gen_ingr_num, verbose_name='Ingredient#')
    vendor_info = models.TextField(blank=True, verbose_name='Vendor Information')
    package_size = models.FloatField(validators=[validate_gt_zero])
    package_size_units = models.CharField(max_length=16,
                                          choices=[('Ounce', 'oz.'), ('Pound', 'lb.'), ('Ton', 'ton.'), ('Gram', 'g.'),
                                                   ('Kilogram', 'kg.'), ('Fluid Ounce', 'fl.oz.'), ('Pint', 'pt.'),
                                                   ('Quart', 'qt.'), ('Gallon', 'gal.'), ('Milliliter', 'mL'),
                                                   ('Liter', 'L'), ('Count', 'count')])
    cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_gt_zero])
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_serializable_string_array(self):
        return [str(self.number), self.name, self.vendor_info, str(self.package_size), self.package_size_units,
                str(self.cost), self.comment]


class ProductLine(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class Formula(models.Model):
    name = models.CharField(max_length=32)
    number = models.IntegerField(unique=True, default=gen_fla_num, verbose_name='Formula#')
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_serializable_string_array(self):
        return [str(self.number), self.name, str(self.comment)]


class SKU(models.Model):
    name = models.CharField(max_length=32)
    sku_num = models.IntegerField(unique=True, default=gen_sku_num, verbose_name='SKU#')
    case_upc = models.CharField(max_length=12, unique=True, validators=[validate_upc], verbose_name='Case UPC')
    unit_upc = models.CharField(max_length=12, validators=[validate_upc], verbose_name='Unit UPC')
    unit_size = models.CharField(max_length=256)
    units_per_case = models.PositiveIntegerField(validators=[validate_gt_zero])
    product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT)
    formula = models.ForeignKey(Formula, on_delete=models.PROTECT)
    formula_scale = models.FloatField(default=1.0, validators=[validate_gt_zero], verbose_name='Formula Scale Factor')
    mfg_rate = models.FloatField(validators=[validate_gt_zero], verbose_name='Manufacturing Rate')
    comment = models.TextField(blank=True)

    def __str__(self):
        return "{name}: {unit_size} * {units_per_case} (SKU#{sku_num})".format(name=self.name, unit_size=self.unit_size, units_per_case=self.units_per_case, sku_num=self.sku_num)

    def get_serializable_string_array(self):
        return [str(self.sku_num), self.name, self.case_upc, self.unit_upc, self.unit_size, str(self.units_per_case),
                self.product_line.name, str(self.formula.number), str(self.formula_scale), str(self.mfg_rate),
                self.comment]


class ManufacturingLine(models.Model):
    name = models.CharField(max_length=32)
    shortname = models.CharField(max_length=5, unique=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return "{name} ({shortname})".format(name=self.name, shortname=self.shortname)


class IngredientQty(models.Model):
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validate_gt_zero])
    quantity_units = models.CharField(max_length=16,
                                      choices=[('Ounce', 'oz.'), ('Pound', 'lb.'), ('Ton', 'ton.'), ('Gram', 'g.'),
                                                 ('Kilogram', 'kg.'), ('Fluid Ounce', 'fl.oz.'), ('Pint', 'pt.'),
                                                 ('Quart', 'qt.'), ('Gallon', 'gal.'), ('Milliliter', 'mL'),
                                                 ('Liter', 'L'), ('Count', 'count')])

    class Meta:
        unique_together = ("formula", "ingredient")

    def clean(self):
        if self.quantity_units in weights and self.ingredient.package_size_units not in weights:
            raise ValidationError("Quantity measured in weight but ingredient package size is not")
        if self.quantity_units in volumes and self.ingredient.package_size_units not in volumes:
            raise ValidationError("Quantity measured in volume but ingredient package size is not")
        if self.quantity_units in counts and self.ingredient.package_size_units not in counts:
            raise ValidationError("Quantity measured in raw count but ingredient package size is not")

    def get_serializable_string_array(self):
        return [str(self.formula.number), str(self.ingredient.number), str(self.quantity)]


class SkuMfgLine(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    mfg_line = models.ForeignKey(ManufacturingLine, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("sku", "mfg_line")
