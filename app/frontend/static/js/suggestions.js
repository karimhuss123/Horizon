export function initSuggestions({
    basketId,
    fetchSuggestionsUrl,
    startJobUrl,
    getJobInProgressUrl,
    getJobUrl,
    renderSuggestions,
    setStatus,
    showPending,
    showSucceeded,
}) {
    async function fetchSuggestions(basketId) {
        const res = await fetch(`${fetchSuggestionsUrl}?basket_id=${basketId}`);
        if (!res.ok) return false;
        const data = await res.json();
        if (!data || data.length === 0) {
            return false;
        }
        renderSuggestions(data);
        return true;
    }
    
    async function fetchJobInProgress() {
        const res = await fetch(`${getJobInProgressUrl}?basket_id=${basketId}`);
        if (!res.ok) {
            return null;
        }
        try {
            const data = await res.json();
            return data || null;
        } catch {
            return null;
        }
    }

    async function runSuggestionsGenJob() {
        try {
            const existingJobInProgress = await fetchJobInProgress();
            if (existingJobInProgress && existingJobInProgress.job_id) {
                return existingJobInProgress;
            }
        } catch (err) {
            console.error('Failed to check existing job.');
        }
        
        try {
            const res = await fetch(startJobUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ basket_id: basketId })
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                const msg = data?.detail?.message || 'Suggestions generation failed. Please try again.';
                setStatus(msg);
                return null;
            };
            return data
        } catch (err) {
            console.error(err);
            setStatus('Suggestions generation failed. Please try again.');
            return null;
        }
    
    }

    async function pollJob(jobId) {
        try {
            const res = await fetch(`${getJobUrl}?id=${jobId}`);
            const data = await res.json().catch(() => ({}));;
            if (!res.ok) {
                const msg = data?.detail?.message || 'Job not found.';
                throw new Error(msg);
            }
            if (data.status === 'pending' || data.status === 'running') {
                setTimeout(() => pollJob(jobId), 2000);
                return;
            }
            if (data.status === 'succeeded') {
                await fetchSuggestions(basketId);
                showSucceeded();
            } else if (data.status === 'failed') {
                const msg = data.error_message || 'Suggestions generation failed. Please try again.';
                setStatus(msg);
            }
            return;
        } catch (err) {
            console.error(err);
            setStatus('Suggestions generation failed. Please try again.');
        }
    }

    // Entry point per page
    (async () => {
        const hasSuggestions = await fetchSuggestions(basketId);
        if (hasSuggestions) return;
        showPending();
        const job = await runSuggestionsGenJob();
        if (job && job.job_id) {
            pollJob(job.job_id);
        } else {
            setStatus("Suggestions generation failed. Please try again.");
        }
    })();
}