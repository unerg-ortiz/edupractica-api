"""
Script to populate the database with sample stages for testing.
This demonstrates the locked stages feature.
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.stage import Stage
from app.crud import crud_stage


def create_sample_stages(db: Session, category_id: int):
    """Create sample stages for a category"""
    
    stages_data = [
        {
            "category_id": category_id,
            "order": 1,
            "title": "Introducción a Python",
            "description": "Aprende los conceptos básicos de Python",
            "content": """
            # Bienvenido a Python
            
            En esta primera etapa aprenderás:
            - Variables y tipos de datos
            - Operadores básicos
            - Entrada y salida de datos
            
            Python es un lenguaje de programación versátil y fácil de aprender.
            """,
            "challenge_description": "Crea un programa que pida tu nombre y edad, y muestre un mensaje de bienvenida personalizado.",
            "is_active": True
        },
        {
            "category_id": category_id,
            "order": 2,
            "title": "Estructuras de Control",
            "description": "Domina if, elif, else y bucles",
            "content": """
            # Estructuras de Control
            
            Aprenderás a:
            - Usar condicionales (if, elif, else)
            - Implementar bucles (for, while)
            - Controlar el flujo con break y continue
            
            Estas estructuras te permiten tomar decisiones en tu código.
            """,
            "challenge_description": "Crea un programa que determine si un número es par o impar, y muestre los primeros 10 números pares.",
            "is_active": True
        },
        {
            "category_id": category_id,
            "order": 3,
            "title": "Funciones",
            "description": "Aprende a crear y usar funciones",
            "content": """
            # Funciones en Python
            
            Las funciones te ayudan a:
            - Organizar tu código
            - Reutilizar lógica
            - Hacer tu código más legible
            
            Aprenderás sobre parámetros, valores de retorno y scope.
            """,
            "challenge_description": "Crea una función que calcule el factorial de un número y otra que determine si un número es primo.",
            "is_active": True
        },
        {
            "category_id": category_id,
            "order": 4,
            "title": "Listas y Diccionarios",
            "description": "Trabaja con estructuras de datos",
            "content": """
            # Estructuras de Datos
            
            Dominarás:
            - Listas y sus métodos
            - Diccionarios y sus operaciones
            - List comprehensions
            - Iteración sobre colecciones
            
            Estas estructuras son fundamentales en Python.
            """,
            "challenge_description": "Crea un programa que gestione una lista de estudiantes con sus calificaciones usando diccionarios.",
            "is_active": True
        },
        {
            "category_id": category_id,
            "order": 5,
            "title": "Programación Orientada a Objetos",
            "description": "Aprende POO en Python",
            "content": """
            # POO en Python
            
            Conceptos clave:
            - Clases y objetos
            - Atributos y métodos
            - Herencia
            - Encapsulamiento
            
            La POO te permite modelar problemas del mundo real.
            """,
            "challenge_description": "Crea una clase 'Estudiante' con atributos y métodos, y una clase 'Curso' que gestione múltiples estudiantes.",
            "is_active": True
        }
    ]
    
    created_stages = []
    for stage_data in stages_data:
        from app.schemas.stage import StageCreate
        stage_create = StageCreate(**stage_data)
        stage = crud_stage.create_stage(db, stage_create)
        created_stages.append(stage)
        print(f"✓ Created stage {stage.order}: {stage.title}")
    
    return created_stages


def main():
    """Main function to populate sample data"""
    db = SessionLocal()
    
    try:
        # Check if we have a category to work with
        category = db.query(Category).first()
        
        if not category:
            print("⚠ No categories found. Creating a sample category...")
            category = Category(
                name="Python Básico",
                description="Curso introductorio de Python",
                icon="🐍"
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            print(f"✓ Created category: {category.name}")
        
        # Check if stages already exist for this category
        existing_stages = crud_stage.get_stages_by_category(db, category.id)
        if existing_stages:
            print(f"⚠ Category '{category.name}' already has {len(existing_stages)} stages.")
            response = input("Do you want to create more stages anyway? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        print(f"\nCreating sample stages for category: {category.name}")
        print("-" * 50)
        
        stages = create_sample_stages(db, category.id)
        
        print("-" * 50)
        print(f"\n✓ Successfully created {len(stages)} stages!")
        print(f"\nStages are configured with progressive unlocking:")
        print(f"  - Stage 1 is unlocked by default")
        print(f"  - Each subsequent stage unlocks when the previous one is completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
