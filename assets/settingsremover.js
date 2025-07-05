if (window.location.pathname === "/challenges") {
  const container = document.querySelector('.row > .col-md-12');

  if (container && !document.querySelector('#btn-unblock-page')) {
    // Création d’un wrapper si besoin
    const wrapper = document.createElement('div');
    wrapper.className = "d-flex justify-content-center mb-4";
    wrapper.id = "btn-unblock-wrapper";

    // Création du bouton "Déblocage"
    const button = document.createElement('a');
    button.href = "/plugins/ctfd-attempts-remover/unblock";
    button.className = "btn btn-info text-white shadow rounded-pill px-4 py-2 fw-semibold d-inline-flex align-items-center gap-2 transition";
    button.id = "btn-unblock-page";

    // Icône
    const icon = document.createElement('i');
    icon.className = "fa fa-user-lock action-icon";

    // Texte
    const span = document.createElement('span');
    span.innerText = "Demander un déblocage challenge";

    // Ajout dans le bouton
    button.appendChild(icon);
    button.appendChild(span);

    // Ajout au wrapper
    wrapper.appendChild(button);
    container.prepend(wrapper);

    // Style CSS personnalisé (même effet hover que btn-attempts-page)
    if (!document.querySelector('#custom-unblock-style')) {
      const style = document.createElement('style');
      style.id = 'custom-unblock-style';
      style.innerHTML = `
        .transition {
          transition: all 0.2s ease-in-out;
        }

        #btn-unblock-page:hover {
          background-color: #212529;
        }
      `;
      document.head.appendChild(style);
    }
  }
}
