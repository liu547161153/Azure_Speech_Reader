window.onload = function() {
    const fileInput = document.getElementById('fileInput');
    const textInput = document.getElementById('textInput');
    const encodingSelect = document.getElementById('encodingSelect');
    const readButton = document.getElementById('readButton');
    const apiUrlInput = document.getElementById('apiUrl'); // 新增API接口URL输入框
    const textDisplayContainer = document.getElementById('textDisplayContainer');
    // 获取保存按钮并添加事件监听器
    const saveButton = document.getElementById('saveButton');

    const backToTopButton = document.getElementById('backToTopButton');
    backToTopButton.addEventListener('click', () => {
    window.scrollTo(0, 0);
    });

    let speechRate = 1.0; // 默认语速值
    const rateSlider = document.getElementById('rateSlider');
    const rateValueDisplay = document.getElementById('rateValue'); // 获取显示语速值的元素

    rateSlider.addEventListener('input', function() {
        speechRate = this.value;
        rateValueDisplay.textContent = `${speechRate}`; // 更新显示的语速值
    });

    // 切换控制面板的显示和隐藏
    document.getElementById('toggleControls').addEventListener('click', function(event) {
    document.getElementById('controlsContainer').classList.toggle('hidden');
    event.stopPropagation(); // 阻止事件冒泡
    });

    // 如果点击的是控制面板或按钮以外的地方，关闭控制面板
    document.addEventListener('click', function(event) {
    var controls = document.getElementById('controlsContainer');
    var toggleButton = document.getElementById('toggleControls');

    // 检查点击是否发生在控制面板或控制按钮上
    if (!controls.contains(event.target) && !toggleButton.contains(event.target)) {
        controls.classList.add('hidden');
    }
    });

    // 获取当前网站的基础域名并拼接'/tts'作为API URL
    apiUrlInput.value = window.location.origin + '/tts';

    let isPrefetching = false; // 标记是否已开始预载入
     // 当前播放的段落索引
    let currentPlayingIndex = 0;
    // 存储每个音频对应的文本段落范围
    let audioSegmentsMap = [];

    // Function to get text from file
     // 根据选择的编码读取文件
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        const selectedEncoding = encodingSelect.value;
        if (file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                textInput.value = e.target.result;
            };

            reader.readAsText(file, selectedEncoding);
        }
    });

    // Function to handle read button click
    readButton.addEventListener('click', function() {
        currentIndex = 0;
        textChunks = splitAndReplaceDialogue(textInput.value);
        audioQueue = [];
        isPlaying = false;
        prefetchNextBatch();


    });

    // Custom set of sentence endings
    const sentenceEndings = ["。", "？", "！", ".", "?", "!"];
    // Custom set of dialogue markers
    const dialogueMarkers = ['「', '」', '『', '』'];
    const newDialogueMarker = ['“', '”'];

    // Function to replace dialogue markers, split text, and create segments
    function splitAndReplaceDialogue(text) {
        const dialogueRegex = new RegExp(`[${dialogueMarkers.join('')}]`, 'g');
        const sentenceRegex = new RegExp(`[^${sentenceEndings.join('')}]+[${sentenceEndings.join('')}]`, 'g');

        text = text.replace(dialogueRegex, (match) => {
            return match === dialogueMarkers[0] || match === dialogueMarkers[2] ? newDialogueMarker[0] : newDialogueMarker[1];
        });

        let segments = [];
        let tempSegment = "";
        let insideDialogue = false;


        for (let i = 0, len = text.length; i < len; i++) {
            tempSegment += text[i];

            if (newDialogueMarker.includes(text[i])) {
                insideDialogue = !insideDialogue;
                if (!insideDialogue) {
                    segments.push(tempSegment.trim());
                    tempSegment = "";
                }
            } else if (sentenceEndings.includes(text[i]) && !insideDialogue) {
                segments.push(tempSegment.trim());
                tempSegment = "";
            }
        }

        if (tempSegment.trim() !== "") {
            segments.push(tempSegment.trim());
        }
        updateTextDisplay(segments); // 新增调用
        return segments;
    }

    // Queue to manage audio playback
    let audioQueue = [];
    let isPlaying = false;
    let currentIndex = 0;
    let textChunks = [];
    let currentAudio = null; // 用于保存当前播放的 audio 对象


    function playNextAudio() {

    if (audioQueue.length > 0 && !isPlaying) {
        const audioBlob = audioQueue.shift();
        const url = URL.createObjectURL(audioBlob);
        const audio = new Audio(url);
        currentAudio = audio; // 更新当前 audio 对象
         // 获取当前音频对应的文本段落范围，并高亮
        const segmentsRange = audioSegmentsMap.shift();
        highlightSegmentsRange(segmentsRange.start, segmentsRange.end);
        isPlaying = true;
        audio.play();
        let hasPrefetched = false; // 新增一个本地标记
        audio.addEventListener('timeupdate', function() {
            const currentTime = audio.currentTime;
            const duration = audio.duration;
            if (currentTime / duration > 0.7 && !hasPrefetched && currentIndex < textChunks.length) {
                prefetchNextBatch();
                hasPrefetched = true; // 设置本地标记，避免重复预载入
            }
        });

        audio.onended = function() {
            isPlaying = false;
            currentPlayingIndex++;
            if (audioQueue.length > 0) {
                playNextAudio(); // 继续播放队列中的下一个音频
            } else if (currentIndex < textChunks.length) {
                prefetchNextBatch(); // 如果还有更多文本待处理，调用 prefetchNextBatch
            } else {
                hasPrefetched = false; // 重置预载入标记
            }
        };
    }
}
    // 为暂停/播放按钮添加事件监听器
    const togglePlayButton = document.getElementById('togglePlayButton');
    togglePlayButton.addEventListener('click', () => {
        if (currentAudio) {
            if (currentAudio.paused) {
                currentAudio.play();
                togglePlayButton.textContent = '暂停';
            } else {
                currentAudio.pause();
                togglePlayButton.textContent = '播放';
            }
        }
    });

    function prefetchNextBatch() {

        if (currentIndex < textChunks.length) {
            const batchEndIndex = Math.min(currentIndex + 3, textChunks.length);
            const batch = textChunks.slice(currentIndex, batchEndIndex).join(' ');

            audioSegmentsMap.push({ start: currentIndex, end: batchEndIndex - 1 });
            currentIndex = batchEndIndex; // 更新 currentIndex
             const postData = {
                text: batch,
                rate: speechRate // 添加语速 rate 参数
            };
            console.log("Sending to TTS API:", batch);
            fetch(apiUrlInput.value, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(postData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error from TTS API: ${response.status}`);
                }
                return response.blob();
            })
            .then(audioBlob => {
                audioQueue.push(audioBlob);
                if (!isPlaying && audioQueue.length === 1) {
                    playNextAudio();
                }
                isPrefetching = false; // 预载入完成后重置
            })
            .catch(error => {
                console.error("Error fetching from TTS API:", error);
                isPrefetching = false; // 预载入完成后重置
            });

        }
    }


     // 更新文本显示容器的内容
    function updateTextDisplay(segments) {
        textDisplayContainer.innerHTML = '';
        segments.forEach((segment, index) => {
            const div = document.createElement('div');
            div.textContent = segment;
            div.id = 'segment-' + index;
            textDisplayContainer.appendChild(div);
        });
    }


   // Function to highlight a range of segments
    function highlightSegmentsRange(startIndex, endIndex) {
        // 清除之前的高亮
        document.querySelectorAll('.highlight').forEach(element => {
            element.classList.remove('highlight');
        });

        // 高亮指定范围的文本段落
        for (let i = startIndex; i <= endIndex; i++) {
            const segmentElement = document.getElementById('segment-' + i);
            if (segmentElement) {
                segmentElement.classList.add('highlight');
            }
        }
         // 获取当前播放段落的元素
        const currentSegmentElement = document.getElementById('segment-' + startIndex);
        if (currentSegmentElement) {
            currentSegmentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function saveRemainingText() {
    // 获取未播放的文本
    const remainingText = textChunks.slice(currentIndex).join('\n');

    // 创建一个 Blob 对象
    const blob = new Blob([remainingText], { type: 'text/plain' });
    // 获取当前日期并格式化
    const today = new Date();
    const dateString = today.getFullYear() + "-" + (today.getMonth() + 1).toString().padStart(2, '0') + "-" + today.getDate().toString().padStart(2, '0');

    // 创建一个链接元素用于下载
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = `剩余文本-${dateString}.txt`;

    // 触发下载
    downloadLink.click();

    // 清理：撤销创建的 URL
    URL.revokeObjectURL(downloadLink.href);
    }
    saveButton.addEventListener('click', saveRemainingText);

};