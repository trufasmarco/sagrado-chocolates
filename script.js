let produtosCadastrados = [];
let carrinho = JSON.parse(localStorage.getItem('sagrado_carrinho')) || [];  

function showToast(mensagem) {
  const container = document.getElementById('toast-container');
  if(!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerText = mensagem;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Zoom do Banner
function alternarZoomBanner() {
  const banner = document.getElementById('banner-zoom');
  const overlay = document.getElementById('zoomOverlay');
  
  if (banner && overlay) {
    banner.classList.toggle('zoom-ativo');
    overlay.classList.toggle('ativo');
  }
}

// Carregar produtos da API do Servidor (Neon.tech) com tela de carregamento
async function carregarProdutos() {  
  const container = document.getElementById('produtos-container');  
  const loader = document.getElementById('loaderOverlay');
  if(!container) return; 
  
  try {
      const response = await fetch('/api/produtos');
      produtosCadastrados = await response.json();
      
      container.innerHTML = '';  
      
      if(produtosCadastrados.length === 0) {
          container.innerHTML = '<p style="text-align:center; color:var(--cream); width: 100%;">Nenhum produto cadastrado ainda.</p>';
      } else {
          produtosCadastrados.forEach(p => {  
            container.innerHTML += `  
              <div class="card-produto">  
                <div>  
                  <img src="${p.img}" alt="${p.nome}" loading="lazy">  
                  <h3>${p.nome}</h3>  
                  <p>Recheio gourmet artesanal.</p>  
                </div>  
                <div>  
                  <div class="preco">R$ ${p.preco.toFixed(2).replace('.', ',')}</div>  
                  <button class="btn-comprar" onclick="adicionarAoCarrinho(${p.id})">Adicionar</button>  
                </div>  
              </div>  
            `;  
          }); 
      }
  } catch (error) {
      console.error("Erro ao carregar produtos:", error);
      container.innerHTML = '<p style="text-align:center; color:var(--gold);">Erro ao conectar com o servidor.</p>';
  } finally {
      if(loader) {
          loader.classList.add('ocultar-loader');
          setTimeout(() => loader.style.display = 'none', 500);
      }
  }
}  

function abrirModal(id) {  
  document.getElementById(id).style.display = 'flex';  
}  

function fecharModal(id) {  
  document.getElementById(id).style.display = 'none';  
}  

window.onclick = function(event) {
  if (event.target.classList.contains('modal')) {
    event.target.style.display = "none";
  }
}

function adicionarAoCarrinho(id) {  
  const produto = produtosCadastrados.find(p => p.id === id);  
  if(!produto) return;

  const itemExistente = carrinho.find(item => item.id === id);
  if (itemExistente) {
    itemExistente.quantidade += 1;
  } else {
    carrinho.push({ ...produto, quantidade: 1 });  
  }

  salvarCarrinho();
  atualizarCarrinho();  
  showToast(`Adicionado: ${produto.nome}`);  
}  

function removerDoCarrinho(id) {
  carrinho = carrinho.filter(item => item.id !== id);
  salvarCarrinho();
  atualizarCarrinho();
}

function salvarCarrinho() {
  localStorage.setItem('sagrado_carrinho', JSON.stringify(carrinho));
}

function atualizarCarrinho() {  
  const totalItens = carrinho.reduce((acc, item) => acc + item.quantidade, 0);
  const countElement = document.getElementById('cart-count');
  if(countElement) countElement.innerText = totalItens;  
  
  const container = document.getElementById('itens-carrinho');  
  if(!container) return;
    
  if (carrinho.length === 0) {  
    container.innerHTML = '<p>O carrinho está vazio.</p>';  
    document.getElementById('total-carrinho').innerText = '0,00';  
    return;  
  }  

  container.innerHTML = '';  
  const valorTotal = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);

  carrinho.forEach(item => {  
    const subtotal = item.preco * item.quantidade;
    container.innerHTML += `
      <div class="cart-item">
        <span>${item.quantidade}x ${item.nome}</span>
        <div>
          <strong>R$ ${subtotal.toFixed(2).replace('.', ',')}</strong>
          <button onclick="removerDoCarrinho(${item.id})" title="Remover item">X</button>
        </div>
      </div>
    `;  
  });  
  
  document.getElementById('total-carrinho').innerText = valorTotal.toFixed(2).replace('.', ',');  
}  

function finalizarPedido() {  
  if(carrinho.length === 0) return showToast('Seu carrinho está vazio!');  
  showToast('Pedido finalizado com sucesso!');  
  carrinho = [];  
  salvarCarrinho();
  atualizarCarrinho();  
  fecharModal('modalCarrinho');  
}  

document.addEventListener('DOMContentLoaded', () => {
  carregarProdutos();
  atualizarCarrinho();
});
