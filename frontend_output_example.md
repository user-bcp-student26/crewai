# Ejemplo de salida: Frontend

> Ejemplo ilustrativo para el Issue **Transfer funds**. El contrato de API descrito aquí es un supuesto didáctico, no un contrato aprobado del equipo. En una ejecución real, el agente debe usar el contrato aprobado que reciba en el contexto y registrar cualquier dato faltante como pendiente.

## `frontend_spec.md`

### Objetivo y recorrido

Permitir que una persona transfiera un importe entre dos cuentas propias. El recorrido carga las cuentas disponibles, permite elegir origen y destino, valida el importe, envía la transferencia una sola vez y muestra confirmación o un error comprensible.

1. Al abrir la pantalla se cargan las cuentas disponibles.
2. Si no hay cuentas, se muestra un estado vacío y no se presenta el formulario de transferencia.
3. La persona elige cuenta de origen, cuenta de destino e importe.
4. El cliente valida campos obligatorios, importe mayor que cero y cuentas distintas.
5. Al confirmar, el botón se deshabilita hasta recibir respuesta.
6. Si la API confirma la operación, se muestra el identificador de transferencia. Si la API rechaza la operación, se muestra el mensaje asociado al error y se permite corregir y reintentar.

### Contrato API ilustrativo

Este ejemplo supone `GET /api/accounts`, que devuelve una lista de cuentas con `id` y `displayName`, y `POST /api/transfers`, que recibe `sourceAccountId`, `destinationAccountId` y `amount`. La creación devuelve `transferId`. Un error `INSUFFICIENT_FUNDS` indica saldo insuficiente. Estos nombres y rutas deben sustituirse por los definidos por Arquitectura y Backend antes de integrar.

### Campos, validaciones y mensajes

| Campo | Validación de interfaz | Mensaje |
| --- | --- | --- |
| Cuenta de origen | Obligatoria | Selecciona una cuenta de origen. |
| Cuenta de destino | Obligatoria y distinta de la cuenta de origen | Selecciona una cuenta de destino distinta. |
| Importe | Obligatorio y mayor que cero | Ingresa un importe mayor que cero. |

La validación de saldo y la autorización permanecen en el servidor. El cliente traduce `INSUFFICIENT_FUNDS` a “La cuenta no tiene saldo suficiente para esta transferencia.” Los errores no reconocidos muestran un mensaje genérico sin exponer detalles internos.

### Estados y acciones

- **Carga:** se anuncia “Cargando cuentas…” y se impiden envíos hasta completar la carga.
- **Vacío:** si la lista está vacía, se indica que no hay cuentas disponibles.
- **Listo:** se muestra el formulario y la acción “Transferir”.
- **Envío:** se deshabilita el botón y se anuncia “Procesando transferencia…”. Un segundo envío mientras la petición está activa se ignora.
- **Éxito:** se anuncia la confirmación y el identificador devuelto por la API.
- **Error:** se muestra el mensaje de validación o API junto al formulario, sin borrar los valores ingresados.

### Accesibilidad

Cada control tiene una etiqueta visible asociada. Los errores se vinculan con `aria-describedby`; los mensajes de carga, error y éxito se anuncian con regiones `aria-live`. Se usan controles HTML nativos, operables por teclado. El foco visible se conserva y se refuerza con `:focus-visible`.

### Cómo comprobar el recorrido

Comprobación manual propuesta, no ejecutada:

1. Ejecuta `npm install` y `npm start` desde `output/frontend-angular` con el backend de desarrollo disponible.
2. Devuelve una lista vacía en `GET /api/accounts` y confirma que se muestra el estado vacío.
3. Devuelve dos cuentas y confirma que los selectores muestran sus nombres.
4. Envía el formulario vacío y después un importe cero; confirma que aparecen mensajes y no se envía la petición.
5. Selecciona la misma cuenta en ambos campos; confirma que se bloquea el envío.
6. Envía una transferencia válida y confirma que solo se emite una petición aunque se active repetidamente el botón durante la carga.
7. Devuelve `INSUFFICIENT_FUNDS`; confirma el mensaje de saldo insuficiente y que los datos siguen disponibles para corregirlos.
8. Devuelve un error no reconocido o simula desconexión; confirma el mensaje genérico y que se puede reintentar.
9. Recorre los controles solo con teclado y verifica etiquetas, anuncios de estado y foco visible.

Estado de ejecución de este ejemplo: **NO EJECUTADO**. Los pasos son una propuesta de verificación, no evidencia de pruebas realizadas.

## Código Angular

```typescript
// transfer.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface Account {
  id: string;
  displayName: string;
}

export interface TransferRequest {
  sourceAccountId: string;
  destinationAccountId: string;
  amount: number;
}

export interface TransferResponse {
  transferId: string;
}

@Injectable({ providedIn: 'root' })
export class TransferService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api';

  getAccounts(): Observable<Account[]> {
    return this.http.get<Account[]>(`${this.apiUrl}/accounts`);
  }

  createTransfer(request: TransferRequest): Observable<TransferResponse> {
    return this.http.post<TransferResponse>(`${this.apiUrl}/transfers`, request);
  }
}
```

```typescript
// transfer.component.ts
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Account, TransferService } from './transfer.service';

const differentAccounts: ValidatorFn = (
  control: AbstractControl,
): ValidationErrors | null => {
  const { sourceAccountId, destinationAccountId } = control.value as {
    sourceAccountId?: string;
    destinationAccountId?: string;
  };
  return sourceAccountId && destinationAccountId && sourceAccountId === destinationAccountId
    ? { sameAccount: true }
    : null;
};

@Component({
  selector: 'app-transfer',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './transfer.component.html',
  styleUrl: './transfer.component.css',
})
export class TransferComponent implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly transferService = inject(TransferService);

  readonly form = this.formBuilder.nonNullable.group(
    {
      sourceAccountId: ['', Validators.required],
      destinationAccountId: ['', Validators.required],
      amount: [0, [Validators.required, Validators.min(0.01)]],
    },
    { validators: differentAccounts },
  );

  accounts: Account[] = [];
  loadingAccounts = true;
  submitting = false;
  loadError = '';
  formError = '';
  successMessage = '';

  ngOnInit(): void {
    this.transferService.getAccounts().subscribe({
      next: (accounts) => {
        this.accounts = accounts;
        this.loadingAccounts = false;
      },
      error: () => {
        this.loadingAccounts = false;
        this.loadError = 'No se pudieron cargar las cuentas. Inténtalo de nuevo.';
      },
    });
  }

  submit(): void {
    if (this.submitting || this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting = true;
    this.formError = '';
    this.successMessage = '';
    this.transferService.createTransfer(this.form.getRawValue()).subscribe({
      next: ({ transferId }) => {
        this.successMessage = `Transferencia realizada. Código: ${transferId}.`;
        this.submitting = false;
      },
      error: (error: HttpErrorResponse) => {
        this.formError = error.error?.code === 'INSUFFICIENT_FUNDS'
          ? 'La cuenta no tiene saldo suficiente para esta transferencia.'
          : 'No se pudo completar la transferencia. Revisa los datos e inténtalo de nuevo.';
        this.submitting = false;
      },
    });
  }
}
```

```html
<!-- transfer.component.html -->
<section aria-labelledby="transfer-title">
  <h1 id="transfer-title">Transferir dinero</h1>

  <p *ngIf="loadingAccounts" role="status" aria-live="polite">Cargando cuentas…</p>
  <p *ngIf="loadError" role="alert">{{ loadError }}</p>

  <p *ngIf="!loadingAccounts && !loadError && accounts.length === 0" role="status">
    No hay cuentas disponibles para transferir.
  </p>

  <form *ngIf="!loadingAccounts && !loadError && accounts.length > 0"
        [formGroup]="form" (ngSubmit)="submit()" novalidate>
    <div>
      <label for="sourceAccountId">Cuenta de origen</label>
      <select id="sourceAccountId" formControlName="sourceAccountId"
              aria-describedby="sourceAccountError">
        <option value="">Selecciona una cuenta</option>
        <option *ngFor="let account of accounts" [value]="account.id">
          {{ account.displayName }}
        </option>
      </select>
      <p id="sourceAccountError" *ngIf="form.controls.sourceAccountId.touched && form.controls.sourceAccountId.invalid">
        Selecciona una cuenta de origen.
      </p>
    </div>

    <div>
      <label for="destinationAccountId">Cuenta de destino</label>
      <select id="destinationAccountId" formControlName="destinationAccountId"
              aria-describedby="destinationAccountError">
        <option value="">Selecciona una cuenta</option>
        <option *ngFor="let account of accounts" [value]="account.id">
          {{ account.displayName }}
        </option>
      </select>
      <p id="destinationAccountError"
         *ngIf="form.controls.destinationAccountId.touched && form.controls.destinationAccountId.invalid">
        Selecciona una cuenta de destino.
      </p>
      <p *ngIf="form.touched && form.hasError('sameAccount')" role="alert">
        Selecciona una cuenta de destino distinta.
      </p>
    </div>

    <div>
      <label for="amount">Importe</label>
      <input id="amount" type="number" min="0.01" step="0.01"
             formControlName="amount" aria-describedby="amountError">
      <p id="amountError" *ngIf="form.controls.amount.touched && form.controls.amount.invalid">
        Ingresa un importe mayor que cero.
      </p>
    </div>

    <p *ngIf="formError" role="alert" aria-live="assertive">{{ formError }}</p>
    <p *ngIf="successMessage" role="status" aria-live="polite">{{ successMessage }}</p>

    <button type="submit" [disabled]="submitting || form.invalid">
      {{ submitting ? 'Procesando…' : 'Transferir' }}
    </button>
  </form>
</section>
```

```css
/* transfer.component.css */
:focus-visible {
  outline: 3px solid #145da0;
  outline-offset: 2px;
}

form {
  display: grid;
  gap: 1rem;
  max-width: 32rem;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

input,
select,
button {
  font: inherit;
  min-height: 2.75rem;
}

[role='alert'] {
  color: #a12622;
}
```
