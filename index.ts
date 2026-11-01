export 70%  Neutral / Surface / Text
20%  Blue / Cyan / Violet
10%  Green / Amber / Red / Pink
const foo = 42
:root {
    /* Background */
      --bg-page: #F7F9FF;
        --bg-surface: #FFFFFF;
          --bg-soft: #F1F5FF;
            --bg-elevated: #FFFFFF;

              /* Text */ry: #14213D;
                  --text-secondary: #475569;
                    --text-muted: #64748B;
                      --text-disabled: #94A3B8;
                        --text-inverse: #FFFFFF;

                          /* Border */
                            --border-default: #E2E8F0;
                              --border-soft: #EEF2F7;
                                --border-strong: #CBD5E1;

                                  /* Brand */
                                    --brand-blue: #2563EB;
                                      --brand-blue-hover: #1D4ED8;

                                        --brand-cyan: #0891B2;
                                          --brand-cyan-soft: #CFFAFE;

                                            --brand-violet: #7C3AED;
                                              --brand-violet-hover: #6D28D9;

                                                --brand-purple: #9333EA;
                                                  --brand-pink: #C026D3;

                                                    /* Semantic */
                                                      --success: #15803D;
                                                        --success-bg: #DCFCE7;

                                                          --warning: #B45309;
                                                            --warning-bg: #FEF3C7;

                                                              --danger: #B91C1C;
                                                                --danger-bg: #FEE2E2;

                                                                  --info: #1D4ED8;
                                                                    --info-bg: #DBEAFE;

                                                                      /* DADO */
                                                                        --dado-primary: #7C3AED;
                                                                          --dado-secondary: #2563EB;
                                                                            --dado-glow: #22D3EE;
                                                                            }.dark {
                                                                                /* Background */
                                                                                  --bg-page: #070D1D;
                                                                                    --bg-surface: #0E172A;
                                                                                      --bg-soft: #131F36;
                                                                                        --bg-elevated: #17233B;

                                                                                          /* Text */
                                                                                            --text-primary: #F1F5F9;
                                                                                              --text-secondary: #CBD5E1;
                                                                                                --text-muted: #94A3B8;
                                                                                                  --text-disabled: #64748B;
                                                                                                    --text-inverse: #071432;

                                                                                                      /* Border */
                                                                                                        --border-default: #263550;
                                                                                                          --border-soft: #1E2B43;
                                                                                                            --border-strong: #3B4B68;

                                                                                                              /* Brand */
                                                                                                                --brand-blue: #60A5FA;
                                                                                                                  --brand-blue-hover: #93C5FD;

                                                                                                                    --brand-cyan: #22D3EE;
                                                                                                                      --brand-cyan-soft: #164E63;

                                                                                                                        --brand-violet: #A78BFA;
                                                                                                                          --brand-violet-hover: #C4B5FD;

                                                                                                                            --brand-purple: #C084FC;
                                                                                                                              --brand-pink: #E879F9;

                                                                                                                                /* Semantic */
                                                                                                                                  --success: #4ADE80;
                                                                                                                                    --success-bg: #123524;

                                                                                                                                      --warning: #FBBF24;
                                                                                                                                        --warning-bg: #422F0B;

                                                                                                                                          --danger: #F87171;
                                                                                                                                            --danger-bg: #451A1A;

                                                                                                                                              --info: #60A5FA;
                                                                                                                                                --info-bg: #172554;

                                                                                                                                                  /* DADO */
                                                                                                                                                    --dado-primary: #A78BFA;
                                                                                                                                                      --dado-secondary: #60A5FA;
                                                                                                                                                        --dado-glow: #22D3EE;
                                                                                                                                                        }
                                                                                                                                                        @theme inline {
                                                                                                                                                            --color-page: var(--bg-page);
                                                                                                                                                              --color-surface: var(--bg-surface);
                                                                                                                                                                --color-soft: var(--bg-soft);
                                                                                                                                                                  --color-elevated: var(--bg-elevated);

                                                                                                                                                                    --color-text-primary: var(--text-primary);
                                                                                                                                                                      --color-text-secondary: var(--text-secondary);
                                                                                                                                                                        --color-text-muted: var(--text-muted);

                                                                                                                                                                          --color-border: var(--border-default);

                                                                                                                                                                            --color-brand-blue: var(--brand-blue);
                                                                                                                                                                              --color-brand-cyan: var(--brand-cyan);
                                                                                                                                                                                --color-brand-violet: var(--brand-violet);

                                                                                                                                                                                  --color-success: var(--success);
                                                                                                                                                                                    --color-warning: var(--warning);
                                                                                                                                                                                      --color-danger: var(--danger);
                                                                                                                                                                                      }
                                                                                                                                                                                      
                                                                                                                                                        }
                                                                            }
                                                                            
}