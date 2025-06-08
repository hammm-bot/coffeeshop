// === cart.js ===
// Requires: Toastify.js & SweetAlert2 already loaded

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
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
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        Toastify({
          text: "✅ Menu berhasil ditambahkan ke keranjang",
          duration: 2000,
          gravity: "top",
          position: "right",
          backgroundColor: "#4caf50"
        }).showToast();
        updateCartIcon();
        loadCart();
      } else {
        Toastify({
          text: "❌ Gagal menambahkan ke keranjang",
          duration: 2000,
          gravity: "top",
          position: "right",
          backgroundColor: "#f44336"
        }).showToast();
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
          text: "🗑️ Item berhasil dihapus dari keranjang",
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
  if (jumlahBaru < 1) {
    hapusPesanan(itemId);
    return;
  }

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

  // Tambahkan event listener tombol Checkout
  const btnCheckout = document.getElementById('btnCheckout');
  if (btnCheckout) {
    btnCheckout.addEventListener('click', function() {
      fetch("/menu/checkout/", {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Sembunyikan tombol checkout
          btnCheckout.style.display = 'none';

          // Isi QR code & form di modal
          const qrSection = document.getElementById('qrcode-payment-section');
          if(qrSection) {
            qrSection.innerHTML = data.html_qrcode_form;
          }

          Toastify({
            text: "Checkout berhasil, silakan lanjutkan pembayaran",
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "#4CAF50",
          }).showToast();
        } else {
          alert(data.message || 'Checkout gagal.');
        }
      })
      .catch(() => {
        Toastify({
          text: "Terjadi kesalahan saat checkout",
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#f44336",
        }).showToast();
      });
    });
  }

  // Fungsi dapatkan csrf token dari cookie (pastikan ada satu saja fungsi ini di file)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});