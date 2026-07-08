// audio.js - Retro Chiptune Polyphonic Synthesizer using Web Audio API
class ChiptuneAudio {
    constructor() {
        this.ctx = null;
        this.muted = false;
        this.melodyInterval = null;
        this.isPlaying = false;
        this.fireInterval = null;
        this.tempo = 115; // Slightly slower, more romantic tempo
        this.beatDuration = 60 / this.tempo;
        
        // Channel 1: Lead Melody (Square wave, sweet & prominent)
        this.melodyNotes = [
            ['E', 5, 1], ['G', 5, 1], ['C', 6, 2],
            ['D', 6, 1], ['C', 6, 1], ['B', 5, 2],
            ['A', 5, 1], ['B', 5, 1], ['C', 6, 2],
            ['G', 5, 2], ['E', 5, 2],
            
            ['E', 5, 1], ['G', 5, 1], ['C', 6, 2],
            ['D', 6, 1], ['F', 6, 1], ['E', 6, 2],
            ['D', 6, 2], ['C', 6, 2], ['B', 5, 4],
            
            ['A', 5, 1], ['C', 6, 1], ['E', 6, 2],
            ['D', 6, 1], ['C', 6, 1], ['G', 5, 2],
            ['F', 5, 1], ['G', 5, 1], ['A', 5, 2],
            ['E', 5, 4],
            
            ['F', 5, 1], ['A', 5, 1], ['D', 6, 2],
            ['B', 5, 2], ['G', 5, 2],
            ['C', 6, 4], [null, 0, 2]
        ];

        // Channel 2: Harmony Track (Square wave, softer, running in parallel)
        this.harmonyNotes = [
            ['C', 5, 1], ['E', 5, 1], ['G', 5, 2],
            ['B', 5, 1], ['A', 5, 1], ['G', 5, 2],
            ['F', 5, 1], ['G', 5, 1], ['A', 5, 2],
            ['E', 5, 2], ['C', 5, 2],
            
            ['C', 5, 1], ['E', 5, 1], ['G', 5, 2],
            ['B', 5, 1], ['D', 6, 1], ['C', 6, 2],
            ['B', 5, 2], ['A', 5, 2], ['G', 5, 4],
            
            ['F', 5, 1], ['A', 5, 1], ['C', 6, 2],
            ['B', 5, 1], ['A', 5, 1], ['E', 5, 2],
            ['D', 5, 1], ['E', 5, 1], ['F', 5, 2],
            ['C', 5, 4],
            
            ['D', 5, 1], ['F', 5, 1], ['B', 5, 2],
            ['G', 5, 2], ['F', 5, 2],
            ['E', 5, 4], [null, 0, 2]
        ];

        // Channel 3: Bass Line (Triangle wave, soft, deep foundation)
        this.bassNotes = [
            ['C', 3, 4], ['G', 3, 4], ['A', 3, 4], ['E', 3, 4],
            ['C', 3, 4], ['F', 3, 4], ['G', 3, 4], ['G', 3, 4],
            ['F', 3, 4], ['C', 3, 4], ['F', 3, 4], ['C', 3, 4],
            ['D', 3, 4], ['G', 3, 4], ['C', 3, 4], ['C', 3, 4]
        ];

        // Channel 4: Arpeggio shimmer (Sine wave, very soft sparkle)
        this.arpeggioNotes = [
            ['C', 5, 0.5], ['E', 5, 0.5], ['G', 5, 0.5], ['C', 6, 0.5],
            ['G', 5, 0.5], ['E', 5, 0.5], ['C', 5, 0.5], [null, 0, 0.5],
            ['D', 5, 0.5], ['F', 5, 0.5], ['A', 5, 0.5], ['D', 6, 0.5],
            ['A', 5, 0.5], ['F', 5, 0.5], ['D', 5, 0.5], [null, 0, 0.5],
            ['F', 5, 0.5], ['A', 5, 0.5], ['C', 6, 0.5], ['F', 6, 0.5],
            ['C', 6, 0.5], ['A', 5, 0.5], ['F', 5, 0.5], [null, 0, 0.5],
            ['G', 5, 0.5], ['B', 5, 0.5], ['D', 6, 0.5], ['G', 6, 0.5],
            ['D', 6, 0.5], ['B', 5, 0.5], ['G', 5, 0.5], [null, 0, 0.5]
        ];

        this.frequencies = {
            'C': 16.35, 'C#': 17.32, 'D': 18.35, 'D#': 19.45, 'E': 20.60, 'F': 21.83,
            'F#': 23.12, 'G': 24.50, 'G#': 25.96, 'A': 27.50, 'A#': 29.14, 'B': 30.87
        };
    }

    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    getFrequency(note, octave) {
        if (!note) return 0;
        const baseFreq = this.frequencies[note];
        return baseFreq * Math.pow(2, octave);
    }

    toggleMute() {
        this.muted = !this.muted;
        if (this.muted) {
            this.stopMelody();
            this.stopAmbientFire();
        } else {
            this.init();
            this.startMelody();
        }
        return this.muted;
    }

    playSFX(type) {
        if (this.muted) return;
        this.init();
        const now = this.ctx.currentTime;

        switch (type) {
            case 'click':
                this.playTone(880, 0.05, 'square', 0.08, now);
                break;
                
            case 'drawer':
                // Slide frequency down for a wood sliding creaking noise
                this.playSlidingTone(180, 80, 0.25, 'triangle', 0.15, now);
                // Little latch click at the end
                this.playTone(400, 0.02, 'square', 0.08, now + 0.23);
                break;
                
            case 'tv_on':
                // Squeal of CRT warming up
                this.playSlidingTone(2000, 4000, 0.25, 'sine', 0.05, now);
                // Cute 8-bit static hum & chime
                this.playTone(880, 0.1, 'square', 0.06, now + 0.15); // A5
                this.playTone(1320, 0.15, 'square', 0.06, now + 0.25); // E6
                break;
                
            case 'item':
                // Classic item pick-up fanfare arpeggio
                this.playTone(523.25, 0.06, 'square', 0.08, now); // C5
                this.playTone(659.25, 0.06, 'square', 0.08, now + 0.06); // E5
                this.playTone(783.99, 0.06, 'square', 0.08, now + 0.12); // G5
                this.playTone(1046.50, 0.12, 'square', 0.12, now + 0.18); // C6
                break;
                
            case 'fanfare':
                // Romantic ending anniversary fanfare
                const t = 0.14;
                this.playTone(523.25, t, 'square', 0.12, now); // C5
                this.playTone(659.25, t, 'square', 0.12, now + t); // E5
                this.playTone(783.99, t, 'square', 0.12, now + t*2); // G5
                this.playTone(1046.50, t*2, 'square', 0.15, now + t*3); // C6
                
                this.playTone(880.00, t, 'square', 0.12, now + t*5); // A5
                this.playTone(1046.50, t*3, 'square', 0.15, now + t*6); // C6 (held)
                
                // Polyphonic harmonies underneath
                this.playTone(659.25, t*3, 'triangle', 0.12, now + t*6); // E5
                this.playTone(523.25, t*3, 'triangle', 0.10, now + t*6); // C5
                break;
                
            case 'rustle':
                // Footstep rustle / carpet / grass sound
                this.playNoise(0.06, 0.02, now);
                break;

            case 'step_wood':
                // Short tap on hardwood floor
                this.playTone(200, 0.03, 'triangle', 0.03, now);
                break;

            case 'step_carpet':
                // Soft muffled step on carpet/rug
                this.playNoise(0.04, 0.015, now);
                break;

            case 'page_flip':
                // Paper rustling sound for memory discoveries
                this.playNoise(0.04, 0.04, now);
                this.playNoise(0.03, 0.03, now + 0.06);
                break;
        }
    }

    playTone(freq, duration, type, volume, startTime) {
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gainNode = this.ctx.createGain();
        
        osc.type = type;
        osc.frequency.setValueAtTime(freq, startTime);
        
        gainNode.gain.setValueAtTime(volume, startTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        osc.connect(gainNode);
        gainNode.connect(this.ctx.destination);
        
        osc.start(startTime);
        osc.stop(startTime + duration);
    }

    playSlidingTone(startFreq, endFreq, duration, type, volume, startTime) {
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gainNode = this.ctx.createGain();
        
        osc.type = type;
        osc.frequency.setValueAtTime(startFreq, startTime);
        osc.frequency.exponentialRampToValueAtTime(endFreq, startTime + duration);
        
        gainNode.gain.setValueAtTime(volume, startTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        osc.connect(gainNode);
        gainNode.connect(this.ctx.destination);
        
        osc.start(startTime);
        osc.stop(startTime + duration);
    }

    playNoise(duration, volume, startTime) {
        if (!this.ctx) return;
        const bufferSize = this.ctx.sampleRate * duration;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.value = 350; // Low soft shuffle
        
        const gainNode = this.ctx.createGain();
        gainNode.gain.setValueAtTime(volume, startTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        noise.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.ctx.destination);
        
        noise.start(startTime);
        noise.stop(startTime + duration);
    }

    startMelody() {
        if (this.muted || this.isPlaying) return;
        this.init();
        this.startAmbientFire();
        this.isPlaying = true;
        
        let melodyIndex = 0;
        let harmonyIndex = 0;
        let bassIndex = 0;
        let arpeggioIndex = 0;
        
        let nextMelodyTime = this.ctx.currentTime + 0.1;
        let nextHarmonyTime = this.ctx.currentTime + 0.1;
        let nextBassTime = this.ctx.currentTime + 0.1;
        let nextArpeggioTime = this.ctx.currentTime + 0.1;
        
        const schedule = () => {
            if (!this.isPlaying) return;
            
            const lookAhead = 0.3;
            const now = this.ctx.currentTime;
            
            // Channel 1: Lead Melody
            while (nextMelodyTime < now + lookAhead) {
                const note = this.melodyNotes[melodyIndex];
                const noteName = note[0];
                const octave = note[1];
                const durationSeconds = note[2] * this.beatDuration;
                
                if (noteName) {
                    const freq = this.getFrequency(noteName, octave);
                    this.playTone(freq, durationSeconds - 0.02, 'square', 0.04, nextMelodyTime);
                }
                nextMelodyTime += durationSeconds;
                melodyIndex = (melodyIndex + 1) % this.melodyNotes.length;
            }
            
            // Channel 2: Harmony Track
            while (nextHarmonyTime < now + lookAhead) {
                const note = this.harmonyNotes[harmonyIndex];
                const noteName = note[0];
                const octave = note[1];
                const durationSeconds = note[2] * this.beatDuration;
                
                if (noteName) {
                    const freq = this.getFrequency(noteName, octave);
                    // Harmony is softer
                    this.playTone(freq, durationSeconds - 0.02, 'square', 0.025, nextHarmonyTime);
                }
                nextHarmonyTime += durationSeconds;
                harmonyIndex = (harmonyIndex + 1) % this.harmonyNotes.length;
            }
            
            // Channel 3: Bass Line
            while (nextBassTime < now + lookAhead) {
                const note = this.bassNotes[bassIndex];
                const noteName = note[0];
                const octave = note[1];
                const durationSeconds = note[2] * this.beatDuration;
                
                if (noteName) {
                    const freq = this.getFrequency(noteName, octave);
                    this.playTone(freq, durationSeconds - 0.01, 'triangle', 0.06, nextBassTime);
                }
                nextBassTime += durationSeconds;
                bassIndex = (bassIndex + 1) % this.bassNotes.length;
            }
            
            // Channel 4: Arpeggio shimmer
            while (nextArpeggioTime < now + lookAhead) {
                const note = this.arpeggioNotes[arpeggioIndex];
                const noteName = note[0];
                const octave = note[1];
                const durationSeconds = note[2] * this.beatDuration;
                
                if (noteName) {
                    const freq = this.getFrequency(noteName, octave);
                    this.playTone(freq, durationSeconds - 0.01, 'sine', 0.015, nextArpeggioTime);
                }
                nextArpeggioTime += durationSeconds;
                arpeggioIndex = (arpeggioIndex + 1) % this.arpeggioNotes.length;
            }
            
            this.melodyInterval = setTimeout(schedule, 100);
        };
        
        schedule();
    }

    stopMelody() {
        this.isPlaying = false;
        if (this.melodyInterval) {
            clearTimeout(this.melodyInterval);
            this.melodyInterval = null;
        }
        this.stopAmbientFire();
    }

    startAmbientFire() {
        if (this.muted || this.fireInterval) return;
        this.init();
        
        const crackle = () => {
            if (this.muted || !this.ctx) return;
            const now = this.ctx.currentTime;
            const freq = 300 + Math.random() * 500;
            const dur = 0.03 + Math.random() * 0.04;
            const vol = 0.008 + Math.random() * 0.012;
            
            const bufferSize = Math.floor(this.ctx.sampleRate * dur);
            const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = Math.random() * 2 - 1;
            }
            const noise = this.ctx.createBufferSource();
            noise.buffer = buffer;
            const filter = this.ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.value = freq;
            filter.Q.value = 2;
            const gainNode = this.ctx.createGain();
            gainNode.gain.setValueAtTime(vol, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + dur);
            noise.connect(filter);
            filter.connect(gainNode);
            gainNode.connect(this.ctx.destination);
            noise.start(now);
            noise.stop(now + dur);
            
            this.fireInterval = setTimeout(crackle, 500 + Math.random() * 1500);
        };
        crackle();
    }

    stopAmbientFire() {
        if (this.fireInterval) {
            clearTimeout(this.fireInterval);
            this.fireInterval = null;
        }
    }
}

const GameAudio = new ChiptuneAudio();
