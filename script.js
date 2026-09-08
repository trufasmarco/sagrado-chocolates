// Base de dados simulada
const produtos = [
  { id: 1, nome: "Cone Trufado de Morango Cremoso", preco: 12.00, estoque: 50, img: "https://via.placeholder.com/300x200/8B0000/FFFDD0?text=Morango" },
  { id: 2, nome: "Cone Trufado de Doce de Leite", preco: 11.00, estoque: 45, img: "https://via.placeholder.com/300x200/D4AF37/2D1500?text=Doce+de+Leite" },
  { id: 3, nome: "Cone Trufado de Brigadeiro Gourmet", preco: 10.00, estoque: 60, img: "https://via.placeholder.com/300x200/2D1500/D4AF37?text=Brigadeiro" },
  { id: 4, nome: "Cone Trufado de Beijinho de Coco", preco: 10.00, estoque: 40, img: "https://via.placeholder.com/300x200/FFFDD0/2D1500?text=Coco" },
  { id: 5, nome: "Cone Trufado de Maracujá Tropical", preco: 11.00, estoque: 55, img: "https://via.placeholder.com/300x200/D4AF37/2D1500?text=Maracuja" }
];

// Inicializa carrinho recuperando do Local Storage ou array vazio
let carrinho = JSON.parse(localStorage.getItem('sagrado_carrinho')) || [];  

// Sistema de Toast (Substitui os alerts)
function showToast(mensagem) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerText = mensagem;
  
  container.appendChild(toast);
  
  // Remove do DOM após a animação (3 segundos)
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Renderizar Produtos  
function carregarProdutos() {  
  const container = document.getElementById('produtos-container');  
  if(!container) return; // Evita erro se o JS rodar antes do HTML
  
  container.innerHTML = '';  
  produtos.forEach(p => {  
    container.innerHTML += `  
      <div class="card-produto">  
        <div>  
          <img src="${p.img}" alt="${p.nome}" loading="lazy">  
          <h3>${p.nome}</h3>  
          <p>Recheio gourmet artesanal de altíssima qualidade.</p>  
        </div>  
        <div>  
          <div class="preco">R$ ${p.preco.toFixed(2).replace('.', ',')}</div>  
          <button class="btn-comprar" onclick="adicionarAoCarrinho(${p.id})">Adicionar ao Carrinho</button>  
        </div>  
      </div>  
    `;  
  });  
}  

// Gerenciar Modais  
function abrirModal(id) {  
  document.getElementById(id).style.display = 'flex';  
  if(id === 'modalAdmin') carregarDashboard();  
}  

function fecharModal(id) {  
  document.getElementById(id).style.display = 'none';  
}  

// Fechar modal clicando fora dele
window.onclick = function(event) {
  if (event.target.classList.contains('modal')) {
    event.target.style.display = "none";
  }
}

// Lógica do Carrinho com Agrupamento e Persistência
function adicionarAoCarrinho(id) {  
  const produto = produtos.find(p => p.id === id);  
  
  // Verifica se o item já existe para aumentar a quantidade
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
  showToast('Item removido do carrinho');
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
  if(carrinho.length === 0) {
    return showToast('Seu carrinho está vazio!');  
  }
  
  showToast('Pedido realizado com sucesso! Entraremos em contato.');  
  carrinho = [];  
  salvarCarrinho();
  atualizarCarrinho();  
  fecharModal('modalCarrinho');  
}  

function handleLogin(event) {
  event.preventDefault();
  showToast('Login efetuado com sucesso!');
  fecharModal('modalLogin');
}

// Lógica do Painel Admin 
function carregarDashboard() {  
  const tabela = document.getElementById('tabela-estoque');  
  if(!tabela) return;

  tabela.innerHTML = '';  
  produtos.forEach(p => {  
    tabela.innerHTML += `  
      <tr>  
        <td>${p.nome}</td>  
        <td>${p.estoque} un</td>  
        <td>R$ ${p.preco.toFixed(2).replace('.', ',')}</td>  
        <td><button style="padding: 4px 8px; cursor: pointer; border-radius: 4px; border: 1px solid var(--gold); background: transparent; color: var(--cream);" onclick="showToast('Edição bloqueada no modo local')">Editar</button></td>  
      </tr>  
    `;  
  });  
}  

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  carregarProdutos();
  atualizarCarrinho();
});
