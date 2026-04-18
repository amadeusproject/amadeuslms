function sendBulk(checkbox) {
  const isChecked = checkbox.checked;
  const currentValue = JSON.parse(checkbox.getAttribute('hx-vals'))

  currentValue.action = isChecked ? 'add' : 'remove';

  checkbox.setAttribute('hx-vals', JSON.stringify(currentValue));

  const childClass = `role-${currentValue.role_id}-ct-${currentValue.content_type_id}`;

  const children = document.querySelectorAll(`.${childClass}`);
  children.forEach(child => {
    child.checked = isChecked;
  });
}
