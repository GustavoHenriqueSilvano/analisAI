document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileUpload');
    const fileList = document.getElementById('fileList');
    const form = document.getElementById('emailForm');

    let selectedFiles = [];

    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if ((file.type === 'text/plain' || file.type === 'application/pdf') && 
                !selectedFiles.some(f => f.name === file.name)) {
                selectedFiles.push(file);
            }
        });
        updateFileList();
    });

    const uploadLabel = document.querySelector('.file-upload-label');
    uploadLabel.addEventListener('dragover', e => { e.preventDefault(); uploadLabel.classList.add('drag-over'); });
    uploadLabel.addEventListener('dragleave', e => { e.preventDefault(); uploadLabel.classList.remove('drag-over'); });
    uploadLabel.addEventListener('drop', e => {
        e.preventDefault();
        uploadLabel.classList.remove('drag-over');
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => {
            if ((file.type === 'text/plain' || file.type === 'application/pdf') &&
                !selectedFiles.some(f => f.name === file.name)) {
                selectedFiles.push(file);
            }
        });
        updateFileList();
    });

    function updateFileList() {
        fileList.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `<span class="file-name">${file.name}</span> <span class="file-size">${formatFileSize(file.size)}</span>`;
            const removeButton = document.createElement('button');
            removeButton.className = 'remove-file';
            removeButton.type = 'button';
            removeButton.textContent = 'Remover';
            removeButton.addEventListener('click', () => {
                selectedFiles.splice(index, 1);
                updateFileList();
            });
            fileItem.appendChild(removeButton);
            fileList.appendChild(fileItem);
        });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const emailContent = document.getElementById('emailContent').value.trim();

        if (!emailContent && selectedFiles.length === 0) {
            alert("Nenhum arquivo ou texto para ser analisado! Por favor, verifique.");
            return;
        }

        const formData = new FormData();
        formData.append('texto', emailContent);
        selectedFiles.forEach(file => formData.append('arquivos', file));

        try {
            const response = await fetch("/analisar", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                const html = await response.text();
                document.open();
                document.write(html);
                document.close();
            } else {
                alert("Erro ao enviar formulário! Status: " + response.status);
            }
        } catch (err) {
            console.error(err);
            alert("Ocorreu um erro ao enviar o formulário!");
        }
    });
});
