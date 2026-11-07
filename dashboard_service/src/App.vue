<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { supabase } from './supabase';

const agents = ref([]);
const now = ref(Date.now());
let timerInterval = null;
let realtimeChannel = null;

// Formateador de tiempo transcurrido (MM:SS o HH:MM:SS)
const formatDuration = (startedAt) => {
if (!startedAt) return '00:00';
const start = new Date(startedAt).getTime();
const diffInSeconds = Math.max(0, Math.floor((now.value - start) / 1000));

const hours = Math.floor(diffInSeconds / 3600);
const minutes = Math.floor((diffInSeconds % 3600) / 60);
const seconds = diffInSeconds % 60;

const pad = (n) => String(n).padStart(2, '0');
if (hours > 0) {
return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}
return `${pad(minutes)}:${pad(seconds)}`;
};

// Cargar estado inicial
const fetchAgentStatus = async () => {
const { data, error } = await supabase
.from('agent_status')
.select('*')
.order('extension', { ascending: true });

if (!error && data) {
agents.value = data;
}
};

onMounted(async () => {
await fetchAgentStatus();

// Actualizador del cronómetro local cada segundo
timerInterval = setInterval(() => {
now.value = Date.now();
}, 1000);

// Escuchar eventos de Supabase Realtime
realtimeChannel = supabase
.channel('realtime:agent_status')
.on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'agent_status' },
    (payload) => {
    const updated = payload.new;
    const index = agents.value.findIndex(a => a.extension === updated.extension);
    if (index !== -1) {
        agents.value[index] = updated;
    } else {
        agents.value.push(updated);
    }
    }
)
.subscribe();
});

onUnmounted(() => {
if (timerInterval) clearInterval(timerInterval);
if (realtimeChannel) supabase.removeChannel(realtimeChannel);
});
</script>

<template>
<div class="min-h-screen bg-slate-950 text-slate-100 p-8">
<div class="max-w-4xl mx-auto space-y-6">

    <header class="border-b border-slate-800 pb-4 flex justify-between items-center">
    <div>
        <h1 class="text-xl font-bold tracking-tight">Monitor de Extensiones</h1>
        <p class="text-xs text-slate-400">Tráfico de llamadas activas en vivo</p>
    </div>
    <div class="flex items-center gap-2">
        <span class="relative flex h-3 w-3">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
        <span class="text-xs text-slate-300 font-medium">AMI Online</span>
    </div>
    </header>

    <!-- Grid de tarjetas de extensión -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
    <div 
        v-for="agent in agents" 
        :key="agent.extension"
        class="rounded-xl p-5 border transition-all duration-300 relative overflow-hidden"
        :class="agent.status === 'IN_CALL' 
        ? 'bg-amber-950/20 border-amber-500/60 shadow-lg shadow-amber-950/20' 
        : 'bg-slate-900 border-slate-800'">
        
        <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
            <span class="text-lg font-bold font-mono tracking-tight text-white">Ext. {{ agent.extension }}</span>
        </div>
        
        <span 
            class="px-2.5 py-0.5 text-xs font-semibold rounded-full border"
            :class="agent.status === 'IN_CALL' 
            ? 'bg-amber-950 text-amber-300 border-amber-700/60 animate-pulse' 
            : 'bg-emerald-950 text-emerald-300 border-emerald-800'">
            {{ agent.status === 'IN_CALL' ? 'En Llamada' : 'Disponible' }}
        </span>
        </div>

        <!-- Información de la llamada -->
        <div v-if="agent.status === 'IN_CALL'" class="space-y-3">
        <div class="flex justify-between items-center text-xs">
            <span class="text-slate-400">Interlocutor:</span>
            <span class="font-mono font-bold text-amber-200 bg-amber-900/40 px-2 py-0.5 rounded border border-amber-800/50">
            Ext. {{ agent.peer_extension }}
            </span>
        </div>

        <!-- Cronómetro en vivo -->
        <div class="flex justify-between items-center text-xs pt-2 border-t border-amber-900/40">
            <span class="text-slate-400">Duración:</span>
            <span class="font-mono text-base font-bold text-amber-400 tracking-wider">
            {{ formatDuration(agent.call_started_at) }}
            </span>
        </div>
        </div>

        <div v-else class="text-xs text-slate-500 flex items-center gap-1.5 pt-2">
        <span class="h-2 w-2 rounded-full bg-emerald-500/50"></span>
        Línea libre y en espera
        </div>

    </div>
    </div>

</div>
</div>
</template>