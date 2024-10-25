$(document).ready(function() {
    $.get("/games", function(data) {
        if (data.error) {
            $("#game-list").html("<p>Erro ao carregar jogos</p>");
        } else {
            let html = "";
            data.forEach(function(game) {
                // Use a imagem de fundo da RAWG, ou uma imagem padrão se não estiver disponível
                const imageUrl = game.background_image || 'imagem_padrao.jpg';

                html += `
                    <div class="col-md-4">
                        <div class="card mb-4">
                            <img src="${imageUrl}" alt="${game.name}" class="card-img-top">
                            <div class="card-body">
                                <h5 class="card-title">${game.name}</h5>
                                <p class="card-text">Data de Lançamento: ${game.released || 'Data não disponível'}</p>
                                <p class="card-text">Gêneros: ${game.genres.map(genre => genre.name).join(', ') || 'Nenhum gênero disponível'}</p>
                            </div>
                        </div>
                    </div>`;
            });
            $("#game-list").html(html);
        }
    }).fail(function() {
        $("#game-list").html("<p>Erro ao carregar jogos</p>");
    });
});
