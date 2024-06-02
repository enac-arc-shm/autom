

const editor = ace.edit('editor', {
	mode: 'ace/mode/json',
	selectionStyle: 'text',
	showPrintMargin: false,
	theme: 'ace/theme/chrome' });
  
  
  const formatText = (spacing = 0) => {
	try {
	  const current = JSON.parse(editor.getValue());
	  editor.setValue(JSON.stringify(current, null, spacing));
	  editor.focus();
	  editor.selectAll();
	  document.execCommand('copy');
	} catch (err) {
	  
	}
  };

  function consultServer() {
	const pathInput = document.getElementById('path');
	const path = pathInput.value;
  
	if (path.trim() === '') {
	  // Manejo de error si el campo de entrada está vacío
	  alert('Por favor, ingrese una ruta de archivo válida.');
	  return;
	}
  
	// Enviar la ruta del archivo al servidor
	fetch(`/consult?path=${encodeURIComponent(path)}`, {
	  method: 'GET'
	})
	.then(response => response.json())
	.then(data => {
	  editor.setValue(data.text); // Establecer el texto en el editor
	})
	.catch(error => {
	  console.error('Error:', error);
	});
  }s
  
  editor.on('paste', event => {
	try {
	  event.text = JSON.stringify(JSON.parse(event.text), null, 4);
	} catch (err) {
	  // meh
	}
  });
  

  function sendEditorContentToServer() {
	const editorContent = editor.getValue(); // Obtener el contenido del editor
	const pathInput = document.getElementById('path');
	const path = pathInput.value;
  
	if (path.trim() === '') {
	  // Manejo de error si el campo de entrada está vacío
	  alert('Por favor, ingrese una ruta de archivo válida.');
	  return;
	}
  
	// Crear una solicitud AJAX utilizando la API Fetch
	fetch(`/save-editor-content?path=${encodeURIComponent(path)}`, {
	  method: 'POST',
	  headers: {
		'Content-Type': 'application/json'
	  },
	  body: JSON.stringify({ content: editorContent })
	})
	.then(response => response.json())
	.then(data => {
	  console.log('Respuesta del servidor:', data);
	  // Aquí puedes manejar la respuesta del servidor si es necesario
	})
	.catch(error => {
	  console.error('Error:', error);
	  // Aquí puedes manejar el error si es necesario
	});
  }


  document.getElementById('minify').addEventListener('click', () => formatText());
  document.getElementById('beautify').addEventListener('click', () => formatText(4));


  