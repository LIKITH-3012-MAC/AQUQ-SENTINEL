/**
 * AquaSentinel AI Marine Debris & Ecosystem Intelligence Controller
 * Handles: image upload → AI inference, map YOLO-style overlays,
 * dashboard evidence cards, detection feed, ecosystem monitoring.
 */

const AIIntelligence = {
    // State
    detectionLayers: null,
    ecosystemLayers: null,
    aiHeatmapLayer: null,
    overlayData: null,
    isLayerActive: false,
    refreshTimer: null,

    // ========= MAP INTEGRATION =========

    /**
     * Initialize AI detection layers on the Leaflet map.
     * @param {L.Map} mapInstance - Leaflet map instance
     */
    initMapLayers(mapInstance) {
        if (!mapInstance || typeof L === 'undefined') return;

        this.map = mapInstance;
        this.detectionLayers = L.layerGroup();
        this.ecosystemLayers = L.layerGroup();
        
        // Start live sync
        this.startIntelligencePolling();
    },

    /**
     * Start automated intelligence synchronization.
     */
    startIntelligencePolling(intervalMs = 30000) {
        if (this.refreshTimer) clearInterval(this.refreshTimer);
        
        // Initial load
        this.loadDashboardIntelligence();
        
        // Background poll
        this.refreshTimer = setInterval(() => {
            console.log("[AI SYNC] Refreshing intelligence feed...");
            this.loadDashboardIntelligence();
            if (this.isLayerActive) this.toggleAIDetections(true);
        }, intervalMs);
    },

    /**
     * Toggle AI Detection overlay on map.
     */
    async toggleAIDetections(enabled) {
        if (!this.map) return;

        if (enabled) {
            try {
                const data = await API.aiDetection.getMapOverlays();
                this.overlayData = data;
                this.detectionLayers.clearLayers();

                if (data.detections && data.detections.length > 0) {
                    data.detections.forEach(det => this._renderDetectionOnMap(det));
                    this.detectionLayers.addTo(this.map);
                    this.isLayerActive = true;
                } else {
                    this._showToast('No AI detections available yet. Upload an image to begin.', 'info');
                }
            } catch (err) {
                console.error('[AI] Detection layer load failure:', err);
            }
        } else {
            this.map.removeLayer(this.detectionLayers);
            this.isLayerActive = false;
        }
    },

    /**
     * Toggle AI Detection heatmap.
     */
    async toggleAIHeatmap(enabled) {
        if (!this.map) return;

        if (enabled) {
            try {
                const data = this.overlayData || await API.aiDetection.getMapOverlays();
                if (this.aiHeatmapLayer) this.map.removeLayer(this.aiHeatmapLayer);

                if (data.heatmap_points && data.heatmap_points.length > 0) {
                    this.aiHeatmapLayer = L.heatLayer(data.heatmap_points, {
                        radius: 30,
                        blur: 20,
                        maxZoom: 12,
                        gradient: {
                            0.2: '#0ea5e9',
                            0.4: '#06b6d4',
                            0.6: '#f59e0b',
                            0.8: '#ef4444',
                            1.0: '#dc2626'
                        }
                    }).addTo(this.map);
                }
            } catch (err) {
                console.error('[AI] Heatmap layer failure:', err);
            }
        } else if (this.aiHeatmapLayer) {
            this.map.removeLayer(this.aiHeatmapLayer);
        }
    },

    /**
     * Toggle Ecosystem Monitoring layer.
     */
    async toggleEcosystemLayer(enabled) {
        if (!this.map) return;

        if (enabled) {
            try {
                const data = this.overlayData || await API.aiDetection.getMapOverlays();
                this.ecosystemLayers.clearLayers();

                if (data.ecosystem_regions) {
                    data.ecosystem_regions.forEach(eco => this._renderEcosystemRegion(eco));
                    this.ecosystemLayers.addTo(this.map);
                }
            } catch (err) {
                console.error('[AI] Ecosystem layer failure:', err);
            }
        } else {
            this.map.removeLayer(this.ecosystemLayers);
        }
    },

    /**
     * Render a single AI detection on the map with YOLO-style visual language.
     */
    _renderDetectionOnMap(det) {
        const severityColor = this._getSeverityColor(det.severity);
        const classLabel = det.debris_class.toUpperCase().replace(/_/g, ' ');
        const confPercent = (det.confidence_score * 100).toFixed(0);

        // 1. Floating AI Label (YOLO-style)
        const labelClass = `ai-map-label severity-${det.severity.toLowerCase()}`;
        const labelIcon = L.divIcon({
            className: 'custom-ai-label',
            html: `<div class="${labelClass}">
                <span class="label-class">${classLabel}</span>
                <span class="label-conf">${confPercent}%</span>
            </div>`,
            iconSize: [0, 0],
            iconAnchor: [0, 0]
        });

        const labelMarker = L.marker([det.latitude, det.longitude], { icon: labelIcon });
        labelMarker.bindPopup(this._buildDetectionPopup(det));
        this.detectionLayers.addLayer(labelMarker);

        // 2. Detection Polygon (Debris Contour)
        if (det.polygon_data && det.polygon_data.length > 0) {
            const coords = det.polygon_data.map(p => [p.lat, p.lon]);
            const polygon = L.polygon(coords, {
                color: severityColor,
                fillColor: severityColor,
                fillOpacity: 0.12,
                weight: 2,
                dashArray: '5, 5',
                className: 'ai-detection-zone-pulse'
            });
            polygon.bindPopup(this._buildDetectionPopup(det));
            this.detectionLayers.addLayer(polygon);
        }

        // 3. Debris Trail Line (Direction indicator)
        if (det.overlay_line_data && det.overlay_line_data.length > 1) {
            const lineCoords = det.overlay_line_data.map(p => [p.lat, p.lon]);
            const polyline = L.polyline(lineCoords, {
                color: severityColor,
                weight: 3,
                opacity: 0.7,
                dashArray: '8, 4'
            });

            // Arrowhead at end of line
            const lastPt = lineCoords[lineCoords.length - 1];
            const arrowMarker = L.circleMarker(lastPt, {
                radius: 4,
                fillColor: severityColor,
                color: severityColor,
                fillOpacity: 0.9,
                weight: 1
            });

            this.detectionLayers.addLayer(polyline);
            this.detectionLayers.addLayer(arrowMarker);
        }

        // 4. Bounding Box (YOLO-style detection rectangle)
        if (det.bbox_like_data) {
            const bbox = det.bbox_like_data;
            const bounds = [
                [bbox.min_lat, bbox.min_lon],
                [bbox.max_lat, bbox.max_lon]
            ];
            const rect = L.rectangle(bounds, {
                color: severityColor,
                fillColor: 'transparent',
                weight: 2,
                opacity: 0.8,
                dashArray: '3, 3'
            });
            this.detectionLayers.addLayer(rect);
        }

        // 5. Confidence Ring
        const ringRadius = 100 + (det.confidence_score * 300); // 100-400m
        const ring = L.circle([det.latitude, det.longitude], {
            radius: ringRadius,
            color: severityColor,
            fillColor: severityColor,
            fillOpacity: 0.05,
            weight: 1,
            opacity: 0.4
        });
        this.detectionLayers.addLayer(ring);
    },

    /**
     * Render an ecosystem monitoring region on the map.
     */
    _renderEcosystemRegion(eco) {
        const color = this._getEcoColor(eco.region_type);

        if (eco.geo_output && eco.geo_output.geometry && eco.geo_output.geometry.coordinates) {
            const coords = eco.geo_output.geometry.coordinates[0].map(c => [c[1], c[0]]);
            const polygon = L.polygon(coords, {
                color: color,
                fillColor: color,
                fillOpacity: 0.2,
                weight: 1.5,
                dashArray: '4, 4'
            });

            polygon.bindPopup(`
                <div style="font-family: 'Outfit'; min-width: 180px;">
                    <div style="font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; color: ${color};">
                        <i class="fas fa-leaf"></i> ECOSYSTEM MONITORING
                    </div>
                    <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 0.5rem;">${eco.region_type.replace(/_/g, ' ').toUpperCase()}</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.75rem; color: var(--text-secondary);">
                        <div><span style="opacity: 0.7;">Confidence:</span> <strong style="color: ${color};">${(eco.confidence_score * 100).toFixed(0)}%</strong></div>
                        <div><span style="opacity: 0.7;">Health:</span> <strong>${eco.ecosystem_health_index?.toFixed(0) || '--'}%</strong></div>
                    </div>
                    ${eco.notes ? `<p style="font-size: 0.7rem; margin-top: 0.5rem; color: var(--text-secondary); opacity: 0.8;">${eco.notes}</p>` : ''}
                </div>
            `);
            this.ecosystemLayers.addLayer(polygon);
        }
    },

    /**
     * Build premium detection popup HTML.
     */
    _buildDetectionPopup(det) {
        const classLabel = det.debris_class.toUpperCase().replace(/_/g, ' ');
        const confPercent = (det.confidence_score * 100).toFixed(1);
        const severityColor = this._getSeverityColor(det.severity);
        const isSim = det.is_simulated;
        const timeStr = new Date(det.created_at).toLocaleString();

        return `
            <div style="font-family: 'Outfit'; min-width: 250px; padding: 0.3rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <span style="font-size: 0.6rem; padding: 0.2rem 0.6rem; border-radius: 50px; background: rgba(0, 243, 255, 0.15); color: #00f3ff; font-weight: 800; letter-spacing: 0.5px;">
                        🤖 AI DEBRIS DETECTION
                    </span>
                    ${isSim ? '<span style="font-size: 0.55rem; padding: 0.15rem 0.5rem; border-radius: 50px; background: rgba(239,68,68,0.2); color: #ef4444; font-weight: 700;">SIMULATED</span>' : '<span style="font-size: 0.55rem; padding: 0.15rem 0.5rem; border-radius: 50px; background: rgba(34,197,94,0.2); color: #22c55e; font-weight: 700;">LIVE</span>'}
                </div>

                <div style="font-weight: 800; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.3rem;">${classLabel}</div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.8rem;">
                    <div>
                        <div style="font-size: 0.55rem; color: var(--text-secondary); text-transform: uppercase;">Confidence</div>
                        <div style="font-size: 1rem; font-weight: 800; color: #00f3ff;">${confPercent}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.55rem; color: var(--text-secondary); text-transform: uppercase;">Severity</div>
                        <div style="font-size: 1rem; font-weight: 800; color: ${severityColor};">${det.severity}</div>
                    </div>
                </div>

                <div style="border-top: 1px solid var(--border-color); padding-top: 0.6rem; font-size: 0.7rem; color: var(--text-secondary);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span>Source:</span> <span style="font-weight: 600;">${det.source_type.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span>Time:</span> <span style="font-weight: 600;">${timeStr}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Location:</span> <span style="font-weight: 600; font-family: monospace;">${det.latitude.toFixed(4)}, ${det.longitude.toFixed(4)}</span>
                    </div>
                </div>

                <div style="margin-top: 0.8rem; padding: 0.5rem 0.8rem; background: rgba(0,243,255,0.05); border-radius: 6px; border: 1px solid rgba(0,243,255,0.1); font-size: 0.65rem; color: #00f3ff; font-weight: 600;">
                    <i class="fas fa-check-circle"></i> Added to Marine Intelligence Pipeline
                </div>
            </div>
        `;
    },

    // ========= DASHBOARD INTEGRATION =========

    /**
     * Load and render AI Intelligence dashboard cards.
     */
    async loadDashboardIntelligence() {
        try {
            const summary = await API.aiDetection.getDashboard();
            this._renderDashboardCards(summary);
            this._renderDetectionFeed(summary.latest_detections);
            this._renderEcosystemSignals(summary.ecosystem_signals);
        } catch (err) {
            console.error('[AI Dashboard] Load failure:', err);
        }
    },

    _renderDashboardCards(summary) {
        const container = document.getElementById('ai-intelligence-stats');
        if (!container) return;

        // Safe defaults
        const stats = {
            today: summary.ai_detections_today ?? 0,
            total: summary.ai_detections_total ?? 0,
            highConf: summary.high_confidence_zones ?? 0,
            avgConf: (summary.avg_detection_confidence ?? 0) * 100,
            ecoAlerts: summary.ecosystem_alerts ?? 0,
            conversions: summary.detection_to_alert_conversions ?? 0
        };

        container.innerHTML = `
            <div class="ai-evidence-stat">
                <div class="value">${stats.today}</div>
                <div class="label">Detections Today</div>
            </div>
            <div class="ai-evidence-stat">
                <div class="value">${stats.total}</div>
                <div class="label">Total Detections</div>
            </div>
            <div class="ai-evidence-stat">
                <div class="value">${stats.highConf}</div>
                <div class="label">High Confidence</div>
            </div>
            <div class="ai-evidence-stat">
                <div class="value">${stats.avgConf.toFixed(0)}%</div>
                <div class="label">Avg Confidence</div>
            </div>
            <div class="ai-evidence-stat">
                <div class="value">${stats.ecoAlerts}</div>
                <div class="label">Eco Alerts</div>
            </div>
            <div class="ai-evidence-stat">
                <div class="value">${stats.conversions}</div>
                <div class="label">Alert Conv.</div>
            </div>
        `;

        // Class distribution bar
        const distBar = document.getElementById('ai-class-distribution');
        if (distBar && summary.debris_class_distribution) {
            const total = Object.values(summary.debris_class_distribution).reduce((a, b) => a + b, 0);
            if (total > 0) {
                const classColors = {
                    plastic_waste: 'plastic',
                    ghost_net: 'ghost_net',
                    floating_debris: 'floating',
                    oil_patch: 'oil',
                    algae_cluster: 'algae',
                    unknown_marine_hazard: 'unknown'
                };
                distBar.innerHTML = Object.entries(summary.debris_class_distribution).map(([cls, cnt]) =>
                    `<div class="class-dist-segment ${classColors[cls] || 'unknown'}" style="width: ${(cnt / total * 100).toFixed(1)}%;" title="${cls}: ${cnt}"></div>`
                ).join('');
            }
        }
    },

    _renderDetectionFeed(detections) {
        const feed = document.getElementById('ai-detection-feed');
        if (!feed) return;

        if (!detections || detections.length === 0) {
            feed.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary); background: rgba(255,255,255,0.01); border-radius: 12px; border: 1px dashed var(--border-color);">
                    <i class="fas fa-satellite-dish" style="font-size: 1.5rem; opacity: 0.3; margin-bottom: 0.8rem; display: block;"></i>
                    <p style="font-size: 0.75rem; font-weight: 500;">No AI detections recorded yet.</p>
                    <p style="font-size: 0.65rem; opacity: 0.6; margin-top: 0.3rem;">Upload a marine image or activate a simulation to begin scanning.</p>
                </div>`;
            return;
        }

        feed.innerHTML = detections.slice(0, 6).map(det => {
            const classLabel = det.debris_class.replace(/_/g, ' ').toUpperCase();
            const confPercent = (det.confidence_score * 100).toFixed(0);
            const severityClass = det.severity.toLowerCase();
            const icon = this._getClassIcon(det.debris_class);
            const timeAgo = this._timeAgo(new Date(det.created_at));

            return `
                <div class="ai-detection-card severity-${severityClass}">
                    <div class="ai-detection-icon">${icon}</div>
                    <div class="ai-detection-content">
                        <div class="ai-detection-class">${classLabel}</div>
                        <div class="ai-detection-meta">
                            <span class="confidence-chip ${severityClass}">${confPercent}% CONF</span>
                            <span>${det.severity}</span>
                            <span>${timeAgo}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    _renderEcosystemSignals(signals) {
        const container = document.getElementById('ai-ecosystem-signals');
        if (!container) return;

        if (!signals || signals.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 1rem; color: var(--text-secondary); opacity: 0.7;">
                    <i class="fas fa-wave-square" style="font-size: 1rem; margin-bottom: 0.5rem; display: block; opacity: 0.3;"></i>
                    <p style="font-size: 0.65rem;">No ecosystem signals detected.</p>
                </div>`;
            return;
        }

        container.innerHTML = signals.slice(0, 4).map(eco => {
            const dotClass = eco.region_type.includes('coral') ? 'coral' :
                             eco.region_type.includes('algae') ? 'algae' :
                             eco.region_type.includes('water') ? 'water' :
                             eco.region_type.includes('polluted') ? 'polluted' : 'stressed';
            const label = eco.region_type.replace(/_/g, ' ').toUpperCase();

            return `
                <div class="eco-status-card">
                    <div class="eco-status-dot ${dotClass}"></div>
                    <div style="flex: 1;">
                        <div style="font-size: 0.75rem; font-weight: 700;">${label}</div>
                        <div style="font-size: 0.65rem; color: var(--text-secondary);">
                            Confidence: ${(eco.confidence_score * 100).toFixed(0)}% | Health: ${eco.ecosystem_health_index?.toFixed(0) || '--'}%
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // ========= IMAGE UPLOAD + DETECTION =========

    /**
     * Handle image upload and AI detection pipeline.
     */
    async handleImageDetection(file, latitude, longitude, locationLabel) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('latitude', latitude);
        formData.append('longitude', longitude);
        if (locationLabel) formData.append('location_label', locationLabel);

        try {
            const result = await API.aiDetection.detectFromImage(formData);
            return result;
        } catch (err) {
            console.error('[AI] Image detection failed:', err);
            throw err;
        }
    },

    // ========= UTILITY FUNCTIONS =========

    _getSeverityColor(severity) {
        const colors = {
            'Critical': '#ef4444',
            'High': '#f59e0b',
            'Medium': '#0ea5e9',
            'Low': '#22c55e'
        };
        return colors[severity] || '#6b7280';
    },

    _getEcoColor(regionType) {
        const colors = {
            'coral_region': '#ff6b9d',
            'algae_region': '#22c55e',
            'water_region': '#0ea5e9',
            'polluted_zone': '#ef4444',
            'stressed_marine_zone': '#f59e0b',
            'sensitive_area': '#a855f7'
        };
        return colors[regionType] || '#6b7280';
    },

    _getClassIcon(debrisClass) {
        const icons = {
            'plastic_waste': '🛢️',
            'ghost_net': '🕸️',
            'floating_debris': '🗑️',
            'oil_patch': '🛢️',
            'algae_cluster': '🌿',
            'unknown_marine_hazard': '⚠️'
        };
        return icons[debrisClass] || '🔍';
    },

    _timeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return `${Math.floor(seconds / 86400)}d ago`;
    },

    _showToast(msg, type) {
        if (typeof UI !== 'undefined' && UI.showNotification) {
            UI.showNotification(msg, type);
        } else {
            console.info(`[AI Toast] ${msg}`);
        }
    }
};
