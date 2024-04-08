function getName(email) {
    // Pull name from before @ in email
    let name = email.split('@')[0];
    return name;
}

