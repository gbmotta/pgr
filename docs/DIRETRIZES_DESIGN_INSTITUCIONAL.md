# Diretrizes de Design Institucional - Sistema PGR

## 1. Arquitetura de Layout

### 1.1 Estrutura Base
```
┌─────────────────────────────────────────────────┐
│ TOPBAR (fixo, altura 48-56px)                   │
├──────────┬──────────────────────────────────────┤
│          │                                       │
│ SIDEBAR  │  CONTENT AREA (full-width)          │
│ (fixo)   │  (scrollable)                        │
│ 240-280px│                                       │
│          │                                       │
└──────────┴──────────────────────────────────────┘
```

### 1.2 Componentes Principais

**Topbar:**
- Altura fixa: 56px
- Background: #1a1a2e (azul escuro institucional) ou #2c3e50 (cinza azulado)
- Conteúdo: Logo/Identificação institucional (esquerda) + Info usuário + Notificações + Logout (direita)
- Sem gradientes, cores sólidas
- Border-bottom: 1px solid #e0e0e0

**Sidebar:**
- Largura fixa: 260px (colapsável para 64px)
- Background: #ffffff
- Border-right: 1px solid #e0e0e0
- Navegação vertical com ícones + labels
- Estado ativo: background #f5f5f5 + border-left 3px #1a1a2e
- Altura: 100vh - 56px (topbar)

**Content Area:**
- Largura: calc(100vw - 260px) quando sidebar expandida
- Padding: 24px (padrão institucional)
- Background: #fafafa (cinza muito claro)
- Sem margens laterais limitantes
- Scroll vertical independente

### 1.3 Breakpoints Responsivos
- Desktop: > 1200px (layout completo)
- Tablet: 768px - 1200px (sidebar colapsável)
- Mobile: < 768px (sidebar overlay)

## 2. Paleta de Cores Institucional

### 2.1 Cores Primárias
```css
--color-primary-dark: #1a1a2e;      /* Azul escuro institucional */
--color-primary: #2c3e50;            /* Cinza azulado */
--color-primary-light: #34495e;      /* Variante mais clara */
--color-accent: #c0392b;             /* Vermelho institucional (alertas críticos) */
--color-accent-secondary: #d68910;  /* Laranja (avisos) */
```

### 2.2 Cores Neutras
```css
--color-bg-primary: #ffffff;         /* Background principal */
--color-bg-secondary: #fafafa;       /* Background secundário */
--color-bg-tertiary: #f5f5f5;       /* Background terciário */
--color-border: #e0e0e0;            /* Bordas padrão */
--color-border-light: #f0f0f0;      /* Bordas sutis */
--color-text-primary: #212121;       /* Texto principal */
--color-text-secondary: #616161;    /* Texto secundário */
--color-text-tertiary: #9e9e9e;     /* Texto terciário */
```

### 2.3 Cores de Status (Jurídico)
```css
--color-status-pendente: #ff9800;   /* Laranja - Pendente */
--color-status-em-analise: #2196f3; /* Azul - Em análise */
--color-status-deferido: #4caf50;   /* Verde - Deferido */
--color-status-indeferido: #f44336; /* Vermelho - Indeferido */
--color-status-vencido: #d32f2f;     /* Vermelho escuro - Vencido */
--color-status-vencendo: #ff6f00;   /* Laranja escuro - Vencendo */
--color-status-ok: #388e3c;         /* Verde escuro - OK */
```

### 2.4 Regras de Uso
- Máximo 2 cores primárias por tela
- Status sempre com cores semânticas consistentes
- Evitar gradientes (exceto sutis em hover states)
- Contraste mínimo WCAG AA (4.5:1 para texto)

## 3. Tipografia

### 3.1 Font Stack
```css
font-family: 
  'Roboto',           /* Primária - legível, profissional */
  'Segoe UI',          /* Fallback Windows */
  -apple-system,       /* Fallback macOS */
  sans-serif;
```

### 3.2 Hierarquia Tipográfica
```css
/* Títulos */
--font-size-h1: 28px;   /* Títulos de página */
--font-size-h2: 22px;   /* Seções principais */
--font-size-h3: 18px;   /* Subseções */
--font-size-h4: 16px;   /* Subtítulos */

/* Corpo */
--font-size-body: 14px;     /* Texto padrão */
--font-size-body-small: 13px; /* Texto secundário */
--font-size-caption: 12px;   /* Legendas, labels */

/* Pesos */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* Line heights */
--line-height-tight: 1.3;
--line-height-normal: 1.5;
--line-height-relaxed: 1.7;
```

### 3.3 Aplicação
- Títulos: font-weight 600-700, cor #212121
- Corpo: font-weight 400, cor #212121
- Labels: font-weight 500, cor #616161, text-transform: uppercase, letter-spacing: 0.5px
- Números/IDs: font-family: 'Courier New', monospace (processos, protocolos)

## 4. Componentes de Interface

### 4.1 Tabelas (Padrão Jurídico)
- Background alternado: #ffffff / #fafafa
- Header: background #f5f5f5, font-weight 600, text-transform uppercase
- Borders: 1px solid #e0e0e0
- Hover: background #f5f5f5
- Densidade: padding vertical 12px, horizontal 16px
- Sem bordas arredondadas excessivas
- Scroll horizontal quando necessário

### 4.2 Cards/Painéis
- Background: #ffffff
- Border: 1px solid #e0e0e0
- Border-radius: 2px (mínimo)
- Shadow: 0 1px 3px rgba(0,0,0,0.1) (sutil)
- Padding: 20px
- Sem gradientes de fundo

### 4.3 Formulários
- Labels: font-weight 500, color #616161, margin-bottom 8px
- Inputs: border 1px solid #e0e0e0, padding 10px 12px, font-size 14px
- Focus: border-color #1a1a2e, outline: none, box-shadow: 0 0 0 2px rgba(26,26,46,0.1)
- Placeholder: color #9e9e9e
- Grupos de campos: margin-bottom 20px

### 4.4 Botões
- Primary: background #1a1a2e, color #ffffff, padding 10px 20px
- Secondary: background transparent, border 1px solid #1a1a2e, color #1a1a2e
- Danger: background #c0392b, color #ffffff
- Hover: opacity 0.9 ou darken 5%
- Sem border-radius excessivo (máximo 4px)
- Font-weight 500

### 4.5 Badges/Status
- Padding: 4px 12px
- Border-radius: 2px
- Font-size: 12px
- Font-weight: 600
- Text-transform: uppercase
- Letter-spacing: 0.5px

## 5. Densidade Informacional

### 5.1 Princípios
- Maximizar informação visível sem scroll
- Agrupar informações relacionadas
- Hierarquia visual clara
- Espaçamento consistente (múltiplos de 4px ou 8px)

### 5.2 Grid System
- Colunas: 12 colunas (flexível)
- Gutter: 16px
- Breakpoints: 1200px, 768px, 480px

### 5.3 Espaçamento
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
```

### 5.4 Tabelas Densas
- Altura de linha: 40-44px (mínimo)
- Múltiplas colunas visíveis simultaneamente
- Sticky headers
- Filtros inline quando possível

## 6. Padrões de Navegação

### 6.1 Sidebar Navigation
- Estrutura hierárquica quando necessário
- Ícones: 20px, cor #616161 (ativo: #1a1a2e)
- Labels: font-size 14px, font-weight 500
- Estado hover: background #f5f5f5
- Estado ativo: background #f5f5f5 + border-left 3px #1a1a2e + color #1a1a2e

### 6.2 Breadcrumbs
- Font-size: 13px
- Separador: / ou >
- Cor: #616161
- Último item: #212121, font-weight 600

### 6.3 Tabs (quando necessário)
- Border-bottom: 2px solid transparent
- Ativo: border-bottom-color #1a1a2e, color #1a1a2e, font-weight 600
- Padding: 12px 20px

## 7. Feedback e Estados

### 7.1 Loading States
- Skeleton screens preferíveis a spinners
- Spinner: cor #1a1a2e, tamanho proporcional ao contexto
- Overlay: background rgba(255,255,255,0.9)

### 7.2 Empty States
- Ícone: 48px, cor #9e9e9e
- Mensagem: font-size 14px, color #616161
- Ação sugerida: botão primary

### 7.3 Notificações/Toasts
- Position: top-right
- Background: #212121 (dark) ou #ffffff (light)
- Border-left: 4px (cor semântica)
- Shadow: 0 4px 12px rgba(0,0,0,0.15)
- Duração: 4s (sucesso), 6s (erro)

## 8. Acessibilidade

### 8.1 Requisitos
- Contraste mínimo WCAG AA
- Focus visible em todos elementos interativos
- Navegação por teclado completa
- ARIA labels quando necessário
- Alt text em ícones informativos

### 8.2 Navegação por Teclado
- Tab order lógico
- Skip links para conteúdo principal
- Atalhos de teclado documentados (opcional)

## 9. Performance Visual

### 9.1 Animações
- Duração máxima: 300ms
- Easing: ease-out ou cubic-bezier(0.4, 0, 0.2, 1)
- Evitar animações desnecessárias
- Preferir transform/opacity sobre position/width/height

### 9.2 Lazy Loading
- Imagens: loading="lazy"
- Componentes pesados: React.lazy()
- Tabelas grandes: virtualização

## 10. Implementação Técnica

### 10.1 Estrutura de Arquivos Recomendada
```
src/
├── components/
│   ├── layout/
│   │   ├── Topbar.jsx
│   │   ├── Sidebar.jsx
│   │   └── Layout.jsx
│   ├── tables/
│   │   ├── DataTable.jsx
│   │   └── TableRow.jsx
│   └── forms/
│       ├── Input.jsx
│       └── Select.jsx
├── styles/
│   ├── variables.css (CSS custom properties)
│   └── components.css (estilos específicos)
└── pages/
```

### 10.2 CSS Custom Properties
Usar variáveis CSS para facilitar manutenção:
```css
:root {
  --color-primary-dark: #1a1a2e;
  --color-primary: #2c3e50;
  /* ... outras variáveis ... */
}
```

### 10.3 Tailwind Config
Extender configuração do Tailwind com cores e espaçamentos customizados:
```js
theme: {
  extend: {
    colors: {
      'institutional': {
        'dark': '#1a1a2e',
        'primary': '#2c3e50',
        // ...
      }
    },
    spacing: {
      // múltiplos de 4 ou 8
    }
  }
}
```

## 11. Checklist de Implementação

### Fase 1: Estrutura Base
- [ ] Criar componente Topbar
- [ ] Criar componente Sidebar
- [ ] Criar componente Layout (composição)
- [ ] Implementar CSS variables
- [ ] Configurar Tailwind com cores institucionais

### Fase 2: Componentes Core
- [ ] DataTable (tabela densa)
- [ ] Form components (Input, Select, etc)
- [ ] Status badges
- [ ] Cards/Painéis

### Fase 3: Páginas
- [ ] Dashboard (redesenhar)
- [ ] Lista de Processos (tabela)
- [ ] Detalhe de Processo
- [ ] Upload
- [ ] Relatórios

### Fase 4: Refinamentos
- [ ] Ajustes de espaçamento
- [ ] Testes de acessibilidade
- [ ] Otimizações de performance
- [ ] Responsividade

## 12. Referências Visuais

### Sistemas de Referência
- Sistemas de tribunais (TJSP, STF)
- Sistemas de procuradorias
- SEI (Sistema Eletrônico de Informações)
- Sistemas governamentais (e-SIC, etc)

### Características Comuns Observadas
- Layouts densos e informativos
- Cores sóbrias e profissionais
- Tipografia clara e legível
- Navegação hierárquica clara
- Foco em funcionalidade sobre estética
- Uso eficiente do espaço vertical e horizontal
