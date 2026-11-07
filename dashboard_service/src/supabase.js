import { createClient } from '@supabase/supabase-js';

// moverlos a env cuando estén en prdod
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://rrxvlnnycowdvyjbizhk.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_yvpmbg9suujpodh4Xw9MkQ_8UAun9ch';

export const supabase = createClient(supabaseUrl, supabaseKey);