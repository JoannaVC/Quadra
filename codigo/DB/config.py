# clase configuracion, conecta a la DB en supabase mediante SQLALCHEMY URI      
class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:#PyF5Fsu_57A@db.qxucdgxslhgcqrcygoaf.supabase.co:5432/postgres?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False