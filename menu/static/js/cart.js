// === cart.js ===
// Requires: Toastify.js & SweetAlert2 already loaded

function getCookie(name) {
  const cookies = document.cookie.split(';').map(c => c.trim());
  for (let cookie of cookies) {
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.split('=')[1]);
    }
  }
  return null;
}

function updateCartIcon() {
  fetch("/menu/cart/")
    .then(res => res.json())
    .then(data => {
      document.querySelector('.cart-count').innerText = data.total_item ?? 0;
    });
}

function loadCart() {
  fetch("/menu/cart/")
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('cart-body');
      const totalEl = document.getElementById('cart-total');
      const container = document.getElementById('cart-container');
      if (!tbody || !totalEl || !container) return;

      if (data.items.length === 0) {
        container.innerHTML = '<div class="alert alert-warning mb-0">Keranjang masih kosong 🛍️</div>';
        return;
      }

      let rows = '';
      data.items.forEach(item => {
        rows += `
          <tr>
            <td>${item.nama}</td>
            <td class="text-center">
              <div class="input-group input-group-sm justify-content-center">
                <button class="btn btn-outline-secondary" onclick="ubahJumlah(${item.id}, ${item.jumlah - 1})">-</button>
                <input type="text" class="form-control text-center" value="${item.jumlah}" readonly style="width: 50px;">
                <button class="btn btn-outline-secondary" onclick="ubahJumlah(${item.id}, ${item.jumlah + 1})">+</button>
              </div>
            </td>
            <td class="text-end">Rp ${item.harga.toLocaleString()}</td>
            <td class="text-end">Rp ${item.subtotal.toLocaleString()}</td>
            <td class="text-center">
              <button class="btn btn-sm btn-danger" onclick="hapusPesanan(${item.id})">
                <i class="fas fa-trash-alt"></i>
              </button>
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = rows;
      totalEl.innerText = `Rp ${data.total.toLocaleString()}`;
    });
}

function tambahKeKeranjang(menuId) {
  fetch(`/menu/add-to-cart/${menuId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ jumlah: 1 })
  })
    .then(res => res.json())
    .then(data => {
      Toastify({
        text: data.status === 'success' ? "✅ Menu berhasil ditambahkan" : "❌ Gagal menambahkan ke keranjang",
        duration: 2000,
        gravity: "top",
        position: "right",
        backgroundColor: data.status === 'success' ? "#4caf50" : "#f44336"
      }).showToast();

      if (data.status === 'success') {
        updateCartIcon();
        loadCart();
      }
    })
    .catch(() => {
      Toastify({
        text: "⚠️ Terjadi kesalahan",
        duration: 2000,
        gravity: "top",
        position: "right",
        backgroundColor: "#f44336"
      }).showToast();
    });
}

function hapusPesanan(itemId) {
  fetch(`/menu/cart/delete/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        Toastify({
          text: "🗑️ Item dihapus",
          duration: 2000,
          gravity: "top",
          position: "right",
          backgroundColor: "#f44336"
        }).showToast();
        updateCartIcon();
        loadCart();
      }
    });
}

function ubahJumlah(itemId, jumlahBaru) {
  if (jumlahBaru < 1) return hapusPesanan(itemId);

  fetch(`/menu/cart/update/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ jumlah: jumlahBaru })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        loadCart();
        updateCartIcon();
      }
    });
}

document.addEventListener('DOMContentLoaded', () => {
  updateCartIcon();

  const cartModal = document.getElementById('cartModal');
  if (cartModal) {
    cartModal.addEventListener('shown.bs.modal', loadCart);
  }

  const btnCheckout = document.getElementById('btnCheckout');
  if (btnCheckout) {
    btnCheckout.addEventListener('click', () => {
      fetch("/menu/checkout/", {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            btnCheckout.style.display = 'none';
            const qrSection = document.getElementById('qrcode-payment-section');
            if (qrSection) qrSection.innerHTML = data.html_qrcode_form;

            Toastify({
              text: "Checkout berhasil, lanjutkan pembayaran",
              duration: 3000,
              gravity: "top",
              position: "right",
              backgroundColor: "#4CAF50"
            }).showToast();
          } else {
            Swal.fire("Checkout gagal", data.message || '', "error");
          }
        })
        .catch(() => {
          Toastify({
            text: "Terjadi kesalahan saat checkout",
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "#f44336"
          }).showToast();
        });
    });
  }

  document.body.addEventListener('submit', function (e) {
    if (e.target && e.target.id === 'formBuktiBayar') {
      e.preventDefault();
      const formData = new FormData(e.target);
      const btnConfirm = document.getElementById('btnConfirmPayment');

      fetch("/menu/upload-bukti/", {
        method: "POST",
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            Toastify({
              text: "✅ Bukti berhasil diupload",
              duration: 3000,
              gravity: "top",
              position: "right",
              backgroundColor: "#4CAF50"
            }).showToast();
            if (btnConfirm) btnConfirm.disabled = false;
          } else {
            Toastify({
              text: `❌ Gagal upload: ${data.message || 'Terjadi kesalahan'}`,
              duration: 3000,
              gravity: "top",
              position: "right",
              backgroundColor: "#f44336"
            }).showToast();
          }
        });
    }
  });

  document.body.addEventListener('click', function (event) {
    if (event.target && event.target.id === 'btnConfirmPayment') {
      const button = event.target;
      if (button.disabled) return; // mencegah klik ulang

      button.disabled = true;
      button.innerText = "Memproses...";

      fetch("/menu/confirm-payment/", {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })
      .then(response => response.json())
      .then(result => {
        if (result.status === 'success') {
          Toastify({ text: "✅ Pembayaran dikonfirmasi!", backgroundColor: "#4CAF50" }).showToast();
          bootstrap.Modal.getInstance(document.getElementById('cartModal')).hide();
          updateCartIcon();
          loadCart();
        } else {
          Toastify({ text: "❌ Gagal konfirmasi", backgroundColor: "#f44336" }).showToast();
        }
      })
      .finally(() => {
        button.disabled = false;
        button.innerText = "Saya sudah bayar";
      });
    }
  });
});