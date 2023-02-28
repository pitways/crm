from app import db

# Create all tables
db.create_all()

# Commit the changes
db.session.commit()

# Close the connection to the database
db.session.close()
