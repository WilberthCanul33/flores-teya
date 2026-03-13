import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organic_veggies.settings')
django.setup()

from apps.catalog.models import Product, Category
from django.core.files import File
from pathlib import Path

def load_products():
    # Crear categorías si no existen
    categories = {
        'verduras': 'Verduras de Hoja Verde',
        'hierbas': 'Hierbas Aromáticas',
        'raices': 'Raíces y Tubérculos',
        'frutas': 'Frutas y Verduras',
    }
    
    category_objects = {}
    for slug, name in categories.items():
        cat, created = Category.objects.get_or_create(name=name, slug=slug)
        category_objects[slug] = cat
        print(f"Categoría {'creada' if created else 'ya existe'}: {name}")
    
    # Ruta base donde están las imágenes
    images_path = Path('media/products/')
    
    # Lista de productos con sus categorías asignadas
    products_data = [
        # (nombre, presentación, precio, propiedades, categoría, nombre_imagen)
        ("ALBAHACA HOJA GRANDE", "PZA", 25, "Vitamina K, algo de A y C, aceites esenciales antioxidantes; digestiva, ligeramente antiinflamatoria y antimicrobiana", "hierbas", "albahaca_hoja_grande.jpeg"),
        ("BERENJENA", "KG", 50, "Muy baja en calorías, buena fibra, potasio y antioxidantes (sobre todo en la piel); apoya digestión, colesterol y salud cardiovascular", "verduras", "berenjena.jpeg"),
        ("HIERBABUENA", "PZA", 15, "Aceites esenciales (mentol) con efecto digestivo, carminativo y refrescante; aporta algo de vitamina A y antioxidantes.", "hierbas", "hierbabuena.jpeg"),
        ("MIX DE LECHUGA", "PZA", 50, "Mucha agua, poca energía, algo de fibra, vitamina A, K y folatos; ideal para hidratación, saciedad y control de peso.", "verduras", "mix_lechuga.jpeg"),
        ("COL MORADA", "KG", 50, "Alta en vitamina C, K y antocianinas; fortalece sistema inmune y ayuda a proteger vasos sanguíneos y corazón.", "verduras", "col_morada.jpeg"),
        ("BOK CHOI", "PZA", 30, "rica en vitamina C, K, calcio, folatos y antioxidantes; favorece salud ósea, defensas y procesos de detoxificación.", "verduras", "bok_choy.jpeg"),
        ("KALE RIZADO", "PZA", 30, "Muy rica en vitamina K, C y A (betacarotenos), además de calcio, hierro y fibra; potente antioxidante y antiinflamatoria.", "verduras", "kale_rizado.jpeg"),
        ("CALABAZA CHIWA", "KG", 50, "Baja en calorías, buena en vitamina C y algo de vitamina A y potasio; ligera, digestiva y diurética suave", "verduras", "calabaza_chiwa.jpeg"),
        ("ALBAHACA LOCAL", "PZA", 15, "Vitamina K y antioxidantes, con efecto digestivo y antimicrobiano suave; muy aromática.", "hierbas", "albahaca_local.jpeg"),
        ("PEREJIL", "PZA", 15, "Muy rico en vitamina C, K, betacarotenos y algo de hierro; fortalece defensas, huesos y es diurético suave", "hierbas", "perejil.jpeg"),
        ("MEJORANA", "PZA", 15, "Hierba aromática con aceites esenciales antioxidantes y antimicrobianos; apoya digestión y relajación ligera", "hierbas", "mejorana.jpeg"),
        ("BETABEL", "PZA", 30, "Aporta folatos, potasio, antioxidantes (betalaínas) y algo de hierro; mejora circulación y ayuda a presión arterial y rendimiento físico", "raices", "betabel.jpeg"),
        ("SALVIA", "PZA", 20, "Contiene compuestos fenólicos y aceites esenciales antioxidantes y antimicrobianos; se usa para digestión y molestias de garganta", "hierbas", "salvia.jpeg"),
        ("CEBOLLA", "PZA", 30, "Fuente de vitamina C y B6, compuestos azufrados antioxidantes y antiinflamatorios; beneficiosa para sistema inmune y corazón", "verduras", "cebolla.jpeg"),
        ("FLOR DE CALABAZA", "PZA", 30, "Muy rica en vitamina A y ácido fólico, con potasio y calcio; baja en calorías, buena para vista, embarazo y defensas", "verduras", "flor_calabaza.jpeg"),
        ("CALABAZA ITALIANA", "KG", 50, "Muy baja en calorías, rica en agua, con vitamina C y algo de vitamina A y potasio; digestiva y ligera.", "verduras", "calabaza_italiana.jpeg"),
        ("TOMATE CHERRY", "PZA", 50, "Vitamina C, vitamina A (licopeno), potasio y antioxidantes; protege corazón, piel y vista.", "frutas", "tomate_cherry.jpeg"),
        ("HOJA SANTA", "PZA", 20, "Hoja aromática con aceites esenciales y antioxidantes; estimula digestión y aporta aroma característico a los platillos.", "hierbas", "hoja_santa.jpeg"),
        ("ELOTE", "PZA", 25, "Aporta fibra, vitamina C, folatos y algo de hierro; bueno para digestión, control de glucosa y salud sanguínea.", "verduras", "elote.jpeg"),
        ("TOMATE UVA", "PZA", 50, "Similar al tomate cherry: rico en vitamina C, A (licopeno) y potasio; apoya defensas y salud cardiovascular.", "frutas", "tomate_uva.jpeg"),
        ("RABANO BLANCO", "KG", 50, "Muy bajo en calorías, rico en vitamina C y compuestos azufrados; digestivo y depurativo suave.", "raices", "rabano_blanco.jpeg"),
        ("OCRA", "PZA", 40, "Buena fuente de fibra soluble, vitamina C, K y folatos; mejora salud intestinal, glucosa y colesterol.", "verduras", "ocra.jpeg"),
        ("ARUGULA", "PZA", 30, "Hoja verde rica en vitamina K, C y folatos; antioxidante, digestiva y con compuestos que apoyan detox hepático.", "verduras", "arugula.jpeg"),
        ("APIO", "PZA", 20, "Muy alto en agua, algo de fibra y potasio; diurético suave, ayuda a presión arterial y digestión.", "verduras", "apio.jpeg"),
        ("BROCOLI", "KG", 50, "Contiene vitamina C, K, folatos, fibra y sulforafano; apoya sistema inmune y protege frente a daño celular.", "verduras", "brocoli.jpeg"),
        ("WASABINA", "PZA", 20, "Hoja tipo mostaza con compuestos azufrados, vitamina C y K; antioxidante, sabor picante, estimula circulación y digestión.", "verduras", "wasabina.jpeg"),
        ("ACELGA", "PZA", 30, "Buena en vitamina A y C, calcio, hierro, magnesio y fibra; favorece sangre, huesos y tránsito intestinal.", "verduras", "acelga.jpeg"),
        ("TOMATE VERDE", "PZA", 50, "Vitamina C, algo de vitamina A y potasio; apoya defensas y salud de la piel.", "frutas", "tomate_verde.jpeg"),
        ("CALABAZA SPAGUETTI", "KG", 70, "Rica en fibra, vitamina A y C, potasio y antioxidantes; ayuda a digestión y sistema inmune con pocas calorías.", "verduras", "calabaza_spaguetti.jpeg"),
        ("MIZUNA", "PZA", 20, "Hoja verde suave-picante con vitamina A, C y K; antioxidante y ligera para mezclas detox.", "verduras", "mizuna.jpeg"),
        ("ALBAHACA GENOVES", "PZA", 20, "Vitamina K, antioxidantes y aceites esenciales digestivos; ideal para pesto y platillos mediterráneos.", "hierbas", "albahaca_genoves.jpeg"),
        ("CAMOTE", "KG", 80, "Carbohidratos complejos, betacarotenos (vitamina A), vitamina C, potasio y fibra; energía estable y fuerte poder antioxidante.", "raices", "camote.jpeg"),
        ("CILANTRO", "PZA", 15, "Aporta vitamina K, C y antioxidantes; favorece digestión, carminativo y con ligero efecto depurativo.", "hierbas", "cilantro.jpeg"),
        ("TAT SOI", "PZA", 30, "Verde asiática rica en vitamina C, K y folatos; baja en calorías y buena para defensas y microbiota.", "verduras", "tatsoi.jpeg"),
        ("DIENTE DE LEON", "PZA", 20, "Aporta vitamina A, C, K y potasio; tradicionalmente depurativa y diurética, apoya hígado y riñones.", "hierbas", "diente_leon.jpeg"),
        ("COLLARD GREEN", "PZA", 20, "Similar a col rizada: mucha vitamina K, C, calcio y fibra; buena para huesos, coagulación y microbiota.", "verduras", "collard_green.jpeg"),
        ("MEI QUIN CHOI", "PZA", 40, "Tipo bok choy: vitamina C, K, folatos y antioxidantes; apoya defensas y salud ósea.", "verduras", "mei_qin_choi.jpeg"),
        ("RABANO NEGRO", "KG", 50, "Rico en vitamina C y compuestos azufrados; depurativo hepático, digestivo y antioxidante.", "raices", "rabano_negro.jpeg"),
        ("KALE LACINATO", "PZA", 30, "Igual que kale rizado: muy rica en vitamina K, C, A, hierro, calcio y fibra; superalimento antioxidante y antiinflamatorio.", "verduras", "kale_lacinato.jpeg"),
        ("CALABAZA BUTTERNUT", "KG", 70, "Alta en betacarotenos (vitamina A), vitamina C, potasio y fibra; muy buena para vista, sistema inmune y digestión.", "verduras", "calabaza_butternut.jpeg"),
        ("COL VERDE", "KG", 50, "Vitamina K, C, folatos y fibra; protege corazón, mejora digestión y ayuda a controlar lípidos.", "verduras", "col_verde.jpeg"),
        ("MOSTAZA", "PZA", 25, "Hoja verde con vitamina A, C, K, calcio y antioxidantes; estimula digestión y aporta compuestos protectores.", "verduras", "mostaza.jpeg"),
        ("NOPAL", "PZA", 40, "Mucha fibra soluble, vitamina C, calcio y antioxidantes; ayuda a controlar glucosa, colesterol y mejora tránsito intestinal.", "verduras", "nopal.jpeg"),
        ("PEPINILLO", "KG", 50, "Altísimo en agua, algo de vitamina K y minerales; hidratante, diurético suave y ligero para el estómago.", "verduras", "pepinillo.jpeg"),
        ("ALBAHACA NAPOLITANA", "PZA", 25, "Vitamina K y compuestos fenólicos antioxidantes; útil para platillos mediterráneos y salud digestiva.", "hierbas", "albahaca_napolitana.jpeg"),
        ("ESCAROLA", "PZA", 30, "Buena en vitamina A y C, fibra y potasio; favorece digestión, saciedad y salud de la piel.", "verduras", "escarola.jpeg"),
    ]
    
    # Obtener lista de nombres válidos
    nombres_validos = [item[0] for item in products_data]
    
    # ELIMINAR productos que ya no están en la lista
    productos_eliminados = 0
    for producto in Product.objects.all():
        if producto.name not in nombres_validos:
            print(f"🗑️ Eliminando producto obsoleto: {producto.name}")
            producto.delete()
            productos_eliminados += 1
    
    # Crear/actualizar productos
    productos_creados = 0
    productos_existentes = 0
    productos_con_imagen = 0
    
    for name, presentation, price, properties, category_slug, image_name in products_data:
        categoria = category_objects.get(category_slug)
        
        if not categoria:
            print(f"⚠️ Categoría no encontrada para {name}: {category_slug}")
            continue
        
        product, created = Product.objects.update_or_create(
            name=name,  # Busca por nombre
            defaults={  # Actualiza estos valores SIEMPRE
                'presentation': presentation,
                'price': price,
                'properties': properties,
                'category': categoria,
                'stock': 10,
                'is_available': True,
                'featured': price <= 30,
            }
        )
        
        # Asignar imagen si existe el archivo
        image_file = images_path / image_name
        if image_file.exists():
            with open(image_file, 'rb') as f:
                product.image.save(image_name, File(f), save=True)
                productos_con_imagen += 1
                print(f"   📸 Imagen asignada: {image_name}")
        else:
            print(f"   ⚠️ Imagen no encontrada: {image_name}")
        
        if created:
            productos_creados += 1
            print(f"✅ Producto NUEVO: {name}")
        else:
            productos_existentes += 1
            print(f"🔄 Producto ACTUALIZADO: {name}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   - Productos eliminados (obsoletos): {productos_eliminados}")
    print(f"   - Productos nuevos creados: {productos_creados}")
    print(f"   - Productos actualizados: {productos_existentes}")
    print(f"   - Productos con imagen: {productos_con_imagen}")
    print(f"   - Total en catálogo: {Product.objects.count()}")

if __name__ == '__main__':
    print("⚠️  Este script SINCRONIZARÁ el catálogo con la lista de productos.")
    print("   - Creará productos nuevos")
    print("   - Actualizará productos existentes")
    print("   - ELIMINARÁ productos que ya no estén en la lista\n")
    
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        load_products()
        print("\n✅ Catálogo sincronizado correctamente.")
    else:
        print("Operación cancelada.")