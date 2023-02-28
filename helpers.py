from werkzeug.exceptions import BadRequest


def validate_client_data(client_data):
    """
    Validates the client data to ensure it's valid before saving to the database.

    :param client_data: A dictionary containing client data.
    :return: None
    :raises: BadRequest if client data is invalid.
    """
    required_fields = ['name', 'email', 'phone']
    for field in required_fields:
        if field not in client_data:
            raise BadRequest(f"Field '{field}' is required.")

    if not client_data['name']:
        raise BadRequest("Name cannot be empty.")

    if not client_data['email']:
        raise BadRequest("Email cannot be empty.")

    if not client_data['phone']:
        raise BadRequest("Phone number cannot be empty.")
