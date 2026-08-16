const sampleInput = document.getElementById('sample');
const fileInput = document.getElementById('fileInput');
const fileNameLabel = document.getElementById('fileNameLabel');
const scanButton = document.getElementById('scanBtn');
const clearButton = document.getElementById('clearBtn');
const charCount = document.getElementById('charCount');
const emptyState = document.getElementById('emptyState');
const resultContent = document.getElementById('resultContent');
const feedback = document.getElementById('feedback');

function updateCount() {
  const count = sampleInput.value.length;
  charCount.textContent = `${count.toLocaleString('fr-FR')} caractère${count === 1 ? '' : 's'}`;
}

function updateSelectedFileName() {
  const selectedFile = fileInput.files && fileInput.files[0];
  fileNameLabel.textContent = selectedFile ? `Fichier sélectionné : ${selectedFile.name}` : 'Aucun fichier sélectionné.';
}

function showResult(data) {
  const isMalicious = data.result === 'malicious';
  const isMedium = data.risk === 'medium';
  const verdictCard = document.getElementById('verdictCard');
  verdictCard.classList.toggle('is-high', isMalicious || data.risk === 'high');
  verdictCard.classList.toggle('is-medium', !isMalicious && isMedium);

  document.getElementById('verdict').textContent = isMalicious ? 'Malveillant' : 'Bénin';
  document.getElementById('verdictDescription').textContent = isMalicious
    ? 'Des indicateurs nécessitent une vérification approfondie.'
    : 'Aucun indicateur critique détecté dans cet échantillon.';
  document.getElementById('score').textContent = `${Math.round(Number(data.score) * 100)} %`;
  document.getElementById('risk').textContent = data.risk === 'low' ? 'Faible' : data.risk === 'medium' ? 'Moyen' : 'Élevé';
  const featureLength = Number(data.features?.length ?? 0);
  document.getElementById('featureLength').textContent = `${featureLength.toLocaleString('fr-FR')} caractères`;
  document.getElementById('featureDigits').textContent = data.features?.num_digits ?? 0;
  document.getElementById('featureLines').textContent = data.features?.num_lines ?? 0;

  const detailList = document.getElementById('riskDetailsList');
  const features = data.features || {};
  const sha256 = data.sha256 || features.sha256 || '—';
  const detectionSignals = [];
  if (features.is_pe) detectionSignals.push('Signature PE détectée');
  if (features.suspicious_extension) detectionSignals.push(`Extension suspecte : ${features.extension || '—'}`);
  if (features.suspicious_hits > 0) detectionSignals.push(`${features.suspicious_hits} indicateurs suspects`);
  if (features.is_binary_like) detectionSignals.push('Structure binaire anormale');
  if (data.hash_known) detectionSignals.push('Hash connu dans la base de référence');

  const items = [
    `Type : ${data.source === 'file' ? (features.is_pe ? 'EXE/PE' : (features.extension || 'fichier')) : 'Texte'}`,
    `SHA256 : ${sha256}`,
    `Méthode : ${data.source === 'file' ? 'analyse de fichier' : 'analyse de texte'}`,
    `Signaux : ${detectionSignals.length ? detectionSignals.join(', ') : 'aucun signal critique'}`
  ];
  detailList.innerHTML = items.map((item) => `<li>${item}</li>`).join('');

  const sourceLabel = data.source === 'file' ? `Fichier ${data.file_name || 'analysé'}` : 'Échantillon texte';
  document.getElementById('resultSubtitle').textContent = `Analyse terminée à l’instant (${sourceLabel}).`;
  emptyState.hidden = true;
  resultContent.hidden = false;
}

async function scanSample() {
  const sample = sampleInput.value.trim();
  const file = fileInput.files && fileInput.files[0];
  feedback.textContent = '';

  if (!sample && !file) {
    feedback.textContent = 'Ajoutez un échantillon texte ou sélectionnez un fichier avant de lancer l’analyse.';
    sampleInput.focus();
    return;
  }

  scanButton.disabled = true;
  scanButton.querySelector('.button-text').textContent = 'Analyse en cours…';
  try {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else {
      formData.append('sample', sample);
    }

    const response = await fetch('/api/scan', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'L’analyse a échoué.');
    showResult(data);
  } catch (error) {
    feedback.textContent = error.message || 'Impossible de joindre le service d’analyse.';
  } finally {
    scanButton.disabled = false;
    scanButton.querySelector('.button-text').textContent = 'Lancer l’analyse';
  }
}

sampleInput.addEventListener('input', updateCount);
fileInput.addEventListener('change', updateSelectedFileName);
scanButton.addEventListener('click', scanSample);
clearButton.addEventListener('click', () => {
  sampleInput.value = '';
  fileInput.value = '';
  updateCount();
  updateSelectedFileName();
  feedback.textContent = '';
  sampleInput.focus();
});
sampleInput.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') scanSample();
});
updateCount();
updateSelectedFileName();
